====================
org.snsoffice.base
====================


Plone 5.0.4 问题
================

* 导航窗口没有显示自定义类型

网站设置=>导航

显示内容类型下选中： Organization, Building, Floor, Room

* 新增菜单中查询集没有对齐问题

Fix collection menu item error indentation in factory menu It changed
by default.css and use !important

    #collection.contenttype-collection {
        padding-left: 50px !important;
    }

* 部分内容没有汉化问题

拷贝 snsgis 里面的 plone.mo 和 widgets.mo，这是以前修改好的

  plone.app.locales-5.0.9-py2.7.egg/plone/app/locales/locales/zh_CN/LC_MESSAGES/plone.mo
  plone.app.locales-5.0.9-py2.7.egg/plone/app/locales/locales/zh_CN/LC_MESSAGES/widgets.mo
