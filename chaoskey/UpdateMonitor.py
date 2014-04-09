# -*- coding: utf-8 -*-# 我的Anki插件# 作者：混沌(youliang@chaoskey.com), http://blog.chaoskey.com# 插件更新检测import re,os,json,time,tracebackfrom datetime import datetimefrom anki.sync import httpConimport aqtfrom aqt import mwfrom aqt.qt import *from aqt.utils import showInfo,showWarningfrom comm import wrap,onLoad,onSwitch,utilsfrom aqt import addonsfrom aqt.addons import GetAddonsglobal weeks,monthsweeks={"Sun":0,"Mon":1,"Tue":2,"Wed":3,"Thu":4,"Fri":5,"Sat":6}months={"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,"Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}# 获取当前已存储的file->code映射数据codeMapping=utils.getConfByKey("addons_code_mapping")if codeMapping:    codeMapping=json.loads(codeMapping)else:    codeMapping={"Chaoskey.py": ["3132534988", round(time.time())+86400]}# 获取当前插件主程序文件列表file_time_map={}dirPath=os.path.realpath(os.path.dirname(__file__)+"\\..")def scan_file_change(check=True):    changed=[]    for f in os.listdir(dirPath):        name = f.split('.')        if len(name) > 1 and name[1] == 'py':            info=os.stat(dirPath+"\\"+f)            if not (file_time_map.has_key(f) and file_time_map[f]==info.st_mtime):                if check:                    changed.append(f)                else:                    file_time_map[f]=info.st_mtime    return changedscan_file_change(False)lastCode=NonelastMT=None# 插件安装监控oldDownload=addons.downloaddef newDownload(_old,_mw,code):    global lastCode,lastMT    con=httpCon()    error=None    try:        head,_=con.request(aqt.appShared + "download/%s"%code,"HEAD")        lastMT=head.get('last-modified')        if not lastMT:            if head['status'] == '200':                error = u"200 但未知原因错误."            elif head['status'] == '403':                error = _("Invalid code.")            else:                error = "Error : %s"%head['status']        else:            lastMT=re.sub("|".join(weeks.keys()),lambda m:str(weeks[m.group(0)]),lastMT)            lastMT=re.sub("|".join(months.keys()),lambda m:str(months[m.group(0)]),lastMT)            lastMT=time.mktime(datetime.strptime(lastMT,'%w, %d %m %Y %H:%M:%S %Z').timetuple())    except Exception, e:        exc = traceback.format_exc()        try:            error = unicode(e[0], "utf8", "ignore")        except:            error = exc    if error:        showWarning(u"网络故障: %s"%error)        return    data,fname=_old(_mw,code)    if code and fname and code not in file_time_map.values():        lastCode=code    return data,fnameoldGetAddonsAccept=GetAddons.acceptdef afterGetAddonsAccept(self):    last_time=time.time()    changed=scan_file_change()    cf=None    lastAbs=None    last_mt=None    global lastCode,lastMT    if lastCode and len(changed):        for f in changed:            info=os.stat(dirPath+"\\"+f)            old_ct=file_time_map.get(f)            if old_ct is None:                cf=f                last_mt=info.st_mtime                break            else:                newAbs=abs(info.st_ctime-old_ct)                if lastAbs is None or newAbs<lastAbs:                    cf=f                    last_mt=info.st_mtime                    lastAbs=newAbs        file_time_map[cf]=last_mt        codeMapping[cf]=[lastCode,lastMT]        utils.setConfByKey("addons_code_mapping",json.dumps(codeMapping))        lastCode=None    lastMT=None            # 插件更新检测checkAddonsTimer=QTimer()def checkAddons():    if hasattr(mw,'col') and mw.col:        con=httpCon()        needUpdates=[]        retry=False        for f,info in codeMapping.items():            if os.path.exists(dirPath+"\\"+f):                try:                    head,_=con.request(aqt.appShared + "download/%s"%info[0],"HEAD")                    m_time=head.get('last-modified')                    if m_time:                        m_time=re.sub("|".join(weeks.keys()),lambda m:str(weeks[m.group(0)]),m_time)                        m_time=re.sub("|".join(months.keys()),lambda m:str(months[m.group(0)]),m_time)                        m_time=time.mktime(datetime.strptime(m_time,'%w, %d %m %Y %H:%M:%S %Z').timetuple())                        if m_time>info[1]:                            needUpdates.append(f)                except:                    retry=True                    break        if not retry:            checkAddonsTimer.stop()        if len(needUpdates)>0:            updateInfo=u"您有下列可升级的Anki插件名及其安装代码：<br /><br />"            for f in needUpdates:                updateInfo+="\t%s\t%s<br />"%(f,codeMapping[f][0])            updateInfo+=u"<br />说明：升级检测只在Anki启动后发生一次."            showInfo(updateInfo)def load():    addons.download = wrap(addons.download, newDownload, "replace")    GetAddons.accept = wrap(GetAddons.accept, afterGetAddonsAccept, "after")    checkAddonsTimer.connect(checkAddonsTimer, SIGNAL('timeout()'), checkAddons)    checkAddonsTimer.start(20000)def unload():    addons.download = oldDownload    GetAddons.accept = oldGetAddonsAccept    checkAddonsTimer.disconnect(checkAddonsTimer, SIGNAL('timeout()'), checkAddons)    checkAddonsTimer.stop()# 本模块的信息ModuleInfo = {'name': u'插件更新检测'}plugName=os.path.basename(__file__).replace(".py", "")# 添加功能开关action=QAction(ModuleInfo["name"], mw)action.setCheckable(True)action.connect(action, SIGNAL("triggered()"),lambda:onSwitch(load,unload,action,plugName))ModuleInfo.update({"action":action})# 功能加载onLoad(load,action,plugName)