# -*- coding: utf-8 -*-# 我的Anki插件# 作者：混沌(youliang@chaoskey.com), http://blog.chaoskey.com# F11全屏from aqt import mwfrom aqt.qt import *from comm import onLoad,onSwitcholdWebMouseMoveEvent=mw.web.mouseMoveEventdef newWebMouseMoveEvent(self,evt):    if mw.windowState() & Qt.WindowFullScreen:        if evt.pos().y()<20:            mw.form.menubar.show()            mw.toolbar.web.show()        elif evt.pos().y()>mw.height()-20:            mw.bottomWeb.show()        else:            mw.form.menubar.hide()            mw.toolbar.web.hide()            mw.bottomWeb.hide()            mw.web.setFocus()    QWebView.mouseMoveEvent(self,evt)# 全屏def onFullScreen():    mw.setWindowState(mw.windowState() ^ Qt.WindowFullScreen)    if mw.windowState() & Qt.WindowFullScreen:        mw.form.menubar.hide()        mw.toolbar.web.hide()        mw.bottomWeb.hide()        mw.web.setMouseTracking(True)    else:        mw.form.menubar.show()        mw.toolbar.web.show()        mw.bottomWeb.show()        mw.web.setMouseTracking(False)fullShortcut=QShortcut(QKeySequence("F11"), mw)def load():    fullShortcut.connect(fullShortcut, SIGNAL("activated()"), onFullScreen)    mw.web.mouseMoveEvent=lambda evt:newWebMouseMoveEvent(mw.web,evt)def unload():    fullShortcut.disconnect(fullShortcut, SIGNAL("activated()"), onFullScreen)    mw.web.mouseMoveEvent=oldWebMouseMoveEvent    if (mw.windowState() & Qt.WindowFullScreen):        onFullScreen()# 本模块的信息ModuleInfo = {'name': u'全屏\tF11'}plugName=os.path.basename(__file__).replace(".py", "")# 添加功能开关action=QAction(ModuleInfo["name"], mw)action.setCheckable(True)action.connect(action, SIGNAL("triggered()"),lambda:onSwitch(load,unload,action,plugName))ModuleInfo.update({"action":action})# 功能加载onLoad(load,action,plugName)