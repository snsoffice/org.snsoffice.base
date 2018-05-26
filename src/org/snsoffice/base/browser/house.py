# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from zope.component import adapter
from zope.container.interfaces import INameChooser
from Products.CMFPlone import utils as ploneutils
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.permissions import AddPortalContent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.dexterity.interfaces import IDXFileFactory
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IUUID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.protect import CheckAuthenticator
from plone.namedfile.utils import safe_basename
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from plone import api

import logging
import mimetypes
import os
import transaction
from zipfile import ZipFile

from org.snsoffice.base.interfaces import IHouseView
from org.snsoffice.base.interfaces import IHouseFeature

class NewHouseWizard(BrowserView):

    index = ViewPageTemplateFile("new_house_wizard.pt")

    def __call__(self):
        return self.index()

class ImportHouseView(BrowserView):
    """导入SweetHome3D生成的房屋结构图，是一个压缩文件，内容如下

    config.json
    views/
        plan/house.jpg
        solid/house.jpg
        three/house.mtl

    其中 config.json 包含下列配置信息


    endpoint: fileUpload
        plone.app.content-3.0.20-py2.7.egg/plone/app/content/browser/file.py

    """
    def __call__(self):
        container = api.content.get(path=self.request.form['form.widgets.building'])
        title = self.request.form['form.widgets.title']
        geolocation = self.request.form['form.widgets.location']
        data = self.request.form['form.widgets.file']
        transaction.begin()
        try:
            house = self.import_entry_from_zip(container, title, geolocation, data)
            transaction.commit()
        except Exception:
            transaction.abort()
            raise
        return json_dumps({
            'name': house.getId(),
            'url': house.absolute_url(),
        })

    def get_file_data(self, value):
        # plone.formwidget.namedfile-1.0.15-py2.7.egg/plone/formwidget/namedfile/converter.py
        filename = safe_basename(value.filename)
        if filename is not None and not isinstance(filename, unicode):
            # Work-around for
            # https://bugs.launchpad.net/zope2/+bug/499696
            filename = filename.decode('utf-8')

        value.seek(0)
        data = value.read()
        return data

    def make_geometry(self, points, origin):
        x0, y0 = origin
        result = []
        for s in points.split(','):
            pt = [float(x) for x in s.split()]
            pt[0] += x0
            pt[1] += y0
            result.append(' '.join([str(x) for x in pt]))
        return ' '.join(['POLYGON ((', ','.join(result), '))'])

    def import_entry_from_zip(self, container, title, geolocation, data):
        f = ZipFile(data, 'r')
        config = json_loads(f.read('config.json'))
        origin = [float(x) for x in geolocation.split(',')]
        house = api.content.create(
            type='House',
            container=container,
            geolocation=geolocation,
            geometry=self.make_geometry(config['points'], origin),
            title=title,
            area=config.get('area'),
            safe_id=True)

        entries = {}
        for x in f.namelist():
            if x.startswith('views/'):
                if x[-1] == '/':
                    k = x.split('/')[-2]
                    entries[k] = []
                else:
                    k = x.split('/')[-2]
                    entries[k].append(x)

        for view in config.get('views', []):
            view_type = view['type']
            house_view = api.content.create(
                type='HouseView',
                container=house,
                view_type=view_type,
                geolocation=geolocation,
                geometry=self.make_geometry(view['points'], origin),
                title=view_type,
                source=view['source'],
                safe_id=True)
            for x in entries.get(view_type, []):
                result = self.import_file(house_view, os.path.basename(x), f.read(x))

        return house

    def import_file(self, container, filename, data):
        content_type = mimetypes.guess_type(filename)[0] or ""

        name = filename.decode("utf8")
        # chooser = INameChooser(container)
        # newid = chooser.chooseName(name, container.aq_parent)
        filename = ploneutils.safe_unicode(name)
        if content_type.startswith('image/'):
            image = NamedBlobImage(
                data=data,
                filename=filename,
                contentType=content_type
            )
            obj = api.content.create(
                type='Image',
                container=container,
                title=name,
                image=image,
                safe_id=True
            )
        else:
            file = NamedBlobFile(
                data=data,
                filename=filename,
                contentType=content_type
            )
            obj = api.content.create(
                type='File',
                container=container,
                title=name,
                file=file,
                safe_id=True
            )
            obj.reindexObject()

        result = {
            "type": '',
            "size": 0
        }

        if 'File' in obj.portal_type:
            result['size'] = obj.file.getSize()
            result['type'] = obj.file.contentType
        elif 'Image' in obj.portal_type:
            result['size'] = obj.image.getSize()
            result['type'] = obj.image.contentType

        result.update({
            'url': obj.absolute_url(),
            'name': obj.getId(),
            'UID': IUUID(obj),
            'filename': filename
        })
        return json_dumps(result)

class HouseFeatureEditor(BrowserView):

    index = ViewPageTemplateFile("house_feature_editor.pt")

    def __call__(self):
        views = []
        features = []
        for v in self.context.contentValues():
            if IHouseView.providedBy(v):
                item = {
                    'name': v.getId(),
                    'type': v.view_type,
                    'opacity': v.opacity,
                    'geometry': v.geometry,
                    'url': v.absolute_url() + '/' + v.source,
                }
                views.append(item)

            elif IHouseFeature.providedBy(v):
                if v.source is None:
                    contentFilter = { "portal_type" : "Image" }
                    images = v.getFolderContents(contentFilter, batch=True, b_size=1)
                    url = images[0].getURL() if len(images) else None
                else:
                    url = v.absolute_url() + '/' + v.source
                item = {
                    'name': v.getId(),
                    'type': v.phase_type,
                    'location': v.geolocation,
                    'angle': v.geoangle,
                    'url': url,
                }
                features.append(item)

        self.house_views = views
        self.house_features = features

        return self.index()
