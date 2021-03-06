# -*- coding: utf-8 -*-
from org.snsoffice.base import _

from zope.component import adapter
from zope.container.interfaces import INameChooser
from Products.CMFPlone import utils as ploneutils
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.permissions import AddPortalContent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.dexterity.interfaces import IDXFileFactory
from plone.dexterity.interfaces import IDexterityFTI
from plone.uuid.interfaces import IUUID
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.protect import CheckAuthenticator
from plone.namedfile.utils import safe_basename
from plone.app.content.utils import json_dumps
from plone.app.content.utils import json_loads
from zope import component
from zope.component.hooks import getSite
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified
from z3c.relationfield import RelationValue
# from z3c.relationfield.relation import create_relation

import logging
import mimetypes
import os
import transaction
from zipfile import ZipFile

from org.snsoffice.base.interfaces import IHouseView
from org.snsoffice.base.interfaces import IHouseFeature

def create_relation(context, path):
    portal_catalog = api.portal.get_tool('portal_catalog')
    intids = component.getUtility(IIntIds)
    # container = api.content.get(path=self.request.form['form.widgets.building'])
    basepath = '/'.join(context.getPhysicalPath()[:2])
    results = portal_catalog(path={
        'query': basepath + path,
        'depth': 0
    })        
    container = results[0].getObject() if results else None
    object_id = intids.getId(container)
    return RelationValue(object_id)

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
        # building= create_relation(self.request.form['form.widgets.building'])
        title = self.request.form['form.widgets.title']
        coordinate = self.request.form['form.widgets.coordinate']
        floor = self.request.form['form.widgets.floor']
        area = self.request.form['form.widgets.area']
        house_type = self.request.form['form.widgets.house_type']
        data = self.request.form['form.widgets.file']
        transaction.begin()
        try:
            building = create_relation(self.context, self.request.form['form.widgets.building'])
            house = self.import_entry_from_zip(building, title, coordinate, data)
            if area:
                house.area = float(area)
            if floor:
                house.floor = int(floor)
            house.house_type = house_type
            modified(house);
            transaction.commit()
            result = {
                'name': house.getId(),
                'url': house.absolute_url(),
            }
        except Exception as e:
            transaction.abort()
            logging.exception('Import house failed');
            result = {
                'error': str(e)
            }
        return json_dumps(result)

    def toFieldValue(self, value):
        catalog = getToolByName(getSite(), 'portal_catalog')
        res = catalog(UID=value)
        if res:
            return res[0].getObject()

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

    def make_multipolygon(self, points, origin):
        x0, y0 = origin
        result = []
        for polygon in points:
            s = []
            for pt in polygon:
                pt[0] += x0
                pt[1] += y0
                s.append(' '.join([str(x) for x in pt]))
            result.append(''.join(['((', ','.join(s), '))']))
        return ''.join(['MULTIPOLYGON (', ','.join(result), ')'])

    def extent_to_polygon(self, extent, origin):
        x, y = origin
        x0 = extent[0] + x
        y0 = extent[1] + y
        x1 = extent[2] + x
        y1 = extent[3] + y
        pts = ['%.2f %.2f' % (x0, y0), '%.2f %.2f' % (x1, y0),
               '%.2f %.2f' % (x1, y1),'%.2f %.2f' % (x0, y1)]
        return ''.join(['POLYGON ((', ','.join(pts), '))'])

    def import_entry_from_zip(self, building, title, coordinate, data):
        f = ZipFile(data, 'r')
        config = json_loads(f.read('config.json'))
        origin = [float(x) for x in coordinate.split(',')]
        house = api.content.create(
            type='House',
            container=self.context,
            building=building,
            coordinate=coordinate,
            geometry=self.make_multipolygon(config['polygons'], origin),
            title=title,
            area=config.get('area'),
            safe_id=True)

        entries = {}
        for x in f.namelist():
            if x.startswith('views/'):
                if x[-1] == '/':
                    continue
                k = x.split('/')[-2]
                try:
                    entries[k].append(x)
                except KeyError:
                    entries[k] = [x]

        for view in config.get('views', []):
            view_type = view['type']
            house_view = api.content.create(
                type='HouseView',
                container=house,
                view_type=view_type,
                coordinate=coordinate,
                geometry=self.extent_to_polygon(view['extent'], origin),
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

    def build_view_url(self, view):
        src = view.source
        if not src:
            contentFilter = { "portal_type" : "Image" }
            images = view.getFolderContents(contentFilter, batch=True, b_size=1)
            url = images[0].getURL() if len(images) else None
        elif src.startswith('http://') or src.startswith('https://'):
            return src
        else:
            return view.absolute_url() + '/' + src

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
                    'url': self.build_view_url(v)
                }
                views.append(item)

            elif IHouseFeature.providedBy(v):
                item = {
                    'name': v.getId(),
                    'type': v.phase_type,
                    'coordinate': v.coordinate,
                    'angle': v.geoangle,
                    'url': self.build_view_url(v),
                }
                features.append(item)

        self.house_views = views
        self.house_features = features

        return self.index()

class NewHouseFeature(BrowserView):
    """创建房屋特征"""

    def __call__(self):
        geoangle = self.request.form['form.widgets.angle']
        coordinate = self.request.form['form.widgets.location']
        phase_type = self.request.form['form.widgets.type']
        source = self.request.form['form.widgets.source']
        filedata = self.request.form['form.widgets.file']
        transaction.begin()
        try:
            feature = api.content.create(
                type='HouseFeature',
                title=_('House Feature'),
                container=self.context,
                coordinate=coordinate,
                geoangle=geoangle,
                phase_type=phase_type,
                source=source,
                safe_id=True
            )
            self.add_image(feature, filedata)
            transaction.commit()
            result = {
                'id': feature.getId(),
                'geoangle': geoangle,
                'coordinate': coordinate,
            }
        except Exception as e:
            transaction.abort()
            result = {
                'error': str(e)
            }
        return json_dumps(result)

    def add_image(self, feature, filedata):
        if filedata is None:
            raise RuntimeError(_('No file data'))

        filename = filedata.filename
        content_type = mimetypes.guess_type(filename)[0] or ""

        name = filename.decode("utf8")
        filename = ploneutils.safe_unicode(name)

        image = NamedBlobImage(
            data=filedata,
            filename=filename,
            contentType=content_type
        )
        obj = api.content.create(
            type='Image',
            container=feature,
            title=name,
            image=image,
            safe_id=True
        )
