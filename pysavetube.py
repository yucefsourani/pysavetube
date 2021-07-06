#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  pysavetube.py
#  
#  Copyright 2021 yucef sourni <youssef.m.sourani@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
#support playlist 
#surport password user and native downloder
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio, GLib, GObject, Pango#, GdkPixbuf
gi.require_version('Adw', '1')
from gi.repository import Adw
import sys
import threading
import urllib.request as request
import os
import sys
import gettext
import json
import importlib
import site
import tarfile
import tempfile
import glob

DATADIR      = GLib.get_user_data_dir()
YOUTYBEDLDIR = os.path.join(DATADIR,"pysavetube") 
HEADERS={"User-Agent":"Mozilla/5.0"}

def load_module(module_file):
    if "youtube_dl" in sys.modules.keys():
        importlib.reload(module)
        return sys.modules["youtube_dl"]
    if module_file.endswith(".py") and os.path.isfile(module_file):
        module_name, module_extension = os.path.splitext(os.path.basename(module_file))
        plugin_folder = os.path.dirname(module_file)
        site.addsitedir(plugin_folder)
        spec   = importlib.util.spec_from_file_location("youtube_dl",module_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    return False
    


module_path = glob.glob(YOUTYBEDLDIR+"/youtube-dl/youtube_dl/__init__.py")
if len(module_path)>0:
    module_path = module_path[0]
    try:
        youtube_dl = load_module(module_path)
        youtub_dl_exists = True
    except:
        youtub_dl_exists = False
else:
    youtub_dl_exists = False


timeout_ = 10
DROPED = ("YouPorn",)

def fix_certifi():
    if getattr(sys, 'frozen',False) and hasattr(sys, '_MEIPASS'):
        import ssl
        if ssl.get_default_verify_paths().cafile is None:
            try:
                import certifi
                cert_l = certifi.where()
                if os.path.isfile(cert_l):
                    os.environ['SSL_CERT_FILE'] = cert_l
                else:
                    os.environ['SSL_CERT_FILE'] = os.path.join(sys._MEIPASS, 'certifi', 'cacert.pem')
            except:
                try:
                    _create_unverified_https_context = ssl._create_unverified_context
                except AttributeError:
                    pass
                else:
                    ssl._create_default_https_context = _create_unverified_https_context
    



def get_correct_path(relative_path):
    if sys.platform.startswith('win'):
        if getattr(sys, 'frozen',False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
    else:
        exedir = os.path.dirname(sys.argv[0])
        p      = os.path.join(exedir,'..', 'share')
        if not os.path.exists(p):
            base_path = exedir
        else :
            base_path = p
            
    return os.path.join(base_path, relative_path)

default_metadata = """{{"current_links"           : [],"current_save_location"   : "{}","timeout" : 10}}
""".format(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS))

win = sys.platform.startswith('win')
if win:
    os.environ['GDK_WIN32_LAYERED'] = "0"
    default_metadata = """{{"current_links"           : [],"current_save_location"   : "{}","timeout" : 10}}
    """.format(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS).replace("\\","/"))
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang

fix_certifi()


gettext.install('pysavetube', localedir=get_correct_path('locale'))

authors_         = ["Youssef Sourani <youssef.m.sourani@gmail.com>"]
version_         = "1.0"
copyright_       = "Copyright © 2020 Youssef Sourani"
comments_        = "Facebook Videos Downloader"
website_         = "https://github.com/yucefsourani/pysavetube"
translators_     = "Arabic Yucef Sourani"
appname          = "pysavetube"
appwindowtitle   = "PySaveTube"
appid            = "com.github.yucefsourani.pysavetube"
icon_            = get_correct_path("pixmaps/com.github.yucefsourani.pysavetube.png")
if not os.path.isfile(icon_):
    icon_ = None



default_metadata_file_name = os.path.join(GLib.get_user_config_dir(),"pysavetube.json")

def get_metadata_info():
    if not os.path.isfile(default_metadata_file_name):
        default_metadata_dict = json.loads(default_metadata)
        with open(default_metadata_file_name,"w",encoding="utf-8") as mf:
            json.dump(default_metadata_dict,mf ,indent=4)
        return get_metadata_info()
    try:
        with open(default_metadata_file_name,encoding="utf-8") as mf:
            result = json.load(mf)
    except Exception as e:
        print(e)
        return False
    return result
    
def change_metadata_info(data):
    if not os.path.isfile(default_metadata_file_name) and os.path.exists(default_metadata_file_name):
        return False
    try:
        with open(default_metadata_file_name,"w",encoding="utf-8") as mf:
            result = json.dump(data,mf ,indent=4)
    except Exception as e:
        print(e)
        return False
    return result
Adw.init()

NETWORKTR    = "network-transmit-receive-symbolic"
NETWORKERROR = "network-error-symbolic"


css = b"""
        .h1 {
            font-size: 24px;
        }
        .h2 {
            font-weight: bold;
            font-size: 18px;
        }
        .h3 {
            font-size: 11px;
        }
        .h4 {
            color: alpha (@text_color, 0.7);
            font-weight: bold;
            text-shadow: 0 1px @text_shadow_color;
        }
        .h4 {
            padding-bottom: 6px;
            padding-top: 6px;
        }
        """

            
class DownloadFile(GObject.Object,threading.Thread):
    __gsignals__ = { "break"     : (GObject.SignalFlags.RUN_LAST, None, ())
    }
    
    def __init__(self,parent,progressbar,button,link,location=None,filename=None,fsize=None,cancel_button=None,close_button=None,mode="w",header={"User-Agent":"Mozilla/5.0"}):
        GObject.Object.__init__(self)
        threading.Thread.__init__(self)
        self.parent        = parent
        self.progressbar   = progressbar
        self.button        = button
        self.link          = link
        self.location      = location
        self.filename      = filename
        self.fsize         = fsize
        self.break_        = False
        self.cancel_button = cancel_button
        self.close_button  = close_button
        self.mode          = mode
        self.header        = header
        self.connect("break",self.on_break)

        
    def on_break(self,s):
        self.break_ = True        
            
    def run(self):
        self.break_ = False
        GLib.idle_add(self.progressbar.show)
        GLib.idle_add(self.button.set_sensitive,False)
        GLib.idle_add(self.close_button.set_sensitive,False)
        saveas_location = os.path.join(self.location,self.filename) 
        ch = 64*1024 
        try:
            with open(saveas_location, self.mode) as op:
                if self.mode == "wb":
                    current_size = 0
                else:
                    op.seek(0,os.SEEK_END)
                    current_size = op.tell()
                psize = current_size
                if current_size == int(self.fsize):
                    GLib.idle_add(self.progressbar.set_fraction,0.0)
                    GLib.idle_add(self.progressbar.set_text,_("Done"))
                    GLib.idle_add(self.button.set_sensitive,True)
                    GLib.idle_add(self.close_button.set_sensitive,True)
                    GLib.idle_add(self.cancel_button.set_sensitive,False)
                    try:
                        op.close()
                    except Exception as e:
                        pass
                    return
                if "Range" in self.header.keys():
                    self.header["Range"] = "bytes={}-{}".format(current_size,self.fsize)
                else:
                    self.header.setdefault("Range", "bytes={}-{}".format(current_size,self.fsize))
                
                url   = request.Request(self.link,headers=self.header)
                opurl = request.urlopen(url,timeout=timeout_)

                while True:
                    if self.break_:
                        GLib.idle_add(self.progressbar.set_fraction,0.0)
                        GLib.idle_add(self.progressbar.set_text,_("Canceled"))
                        GLib.idle_add(self.button.set_sensitive,True)
                        GLib.idle_add(self.close_button.set_sensitive,True)
                        GLib.idle_add(self.cancel_button.set_sensitive,False)
                        try:
                            op.close()
                            opurl.close()
                        except Exception as e:
                            pass
                        return
                    op.flush()
                    if psize >=int(self.fsize):
                        break
                    n = int(self.fsize)-psize
                    if n<ch:
                        ch = n

                    chunk = opurl.read(ch)

                    count = int((psize*100)//int(self.fsize))
                    fraction = count/100
                    op.write(chunk)
                    psize += ch
                    GLib.idle_add(self.progressbar.set_fraction,fraction)
                    GLib.idle_add(self.progressbar.set_text,str(count)+"%"+" "+str(psize)+"/"+str(self.fsize)+" B")
                
            GLib.idle_add(self.progressbar.set_fraction,1.0)
            GLib.idle_add(self.progressbar.set_text,_("Done"))
        except Exception as e:
            print(e)
            GLib.idle_add(self.progressbar.set_fraction,0.0)
            GLib.idle_add(self.progressbar.set_text,_("Fail"))
            GLib.idle_add(self.button.set_sensitive,True)
            GLib.idle_add(self.close_button.set_sensitive,True)
            GLib.idle_add(self.cancel_button.set_sensitive,False)
            return False
        finally:
            try:
                opurl.close()
            except Exception as e:
                pass
            
        GLib.idle_add(self.progressbar.set_fraction,0.0)
        GLib.idle_add(self.button.set_sensitive,True)
        GLib.idle_add(self.close_button.set_sensitive,True)
        GLib.idle_add(self.cancel_button.set_sensitive,False)


class MInfoBarB():
    def __init__(self,parent,message_type,row=None,result=None,func=None):
        self.parent       = parent
        self.message_type = message_type
        self.row          = row
        self.result       = result
        self.func         = func
        self.send_button  = True

        
        self.mainhbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,10)

        self.infobar = Gtk.InfoBar()
        self.infobar.set_show_close_button(True)
        self.infobar.connect("response", self.hide__)
        
        self.label = Gtk.Label()
        self.label.props.label = ""
        self.b = Gtk.Button()
        self.b.props.label = ""
        self.b.connect("clicked",self.on_b_clicked)
        self.mainhbox.append(self.label)
        self.mainhbox.append(self.b)
        self.infobar.add_child(self.mainhbox )
        self.infobar.set_message_type(self.message_type)
        #self.infobar.props.no_show_all = True
        
        self.parent.append(self.infobar)
        self.hide__()

    def on_b_clicked(self,button):
        if self.send_button:
            self.func(button,self.row,self.result,force=True)
        else:
            self.func(self.row,self.result,force=True)
        self.infobar.hide()
        
    def show__(self):
        self.infobar.set_revealed(True)
        self.infobar.show()

    def hide__(self, infobar=None, respose_id=None):
        self.infobar.set_revealed(False)
        self.infobar.hide()
        
class MInfoBar():
    def __init__(self,parent,msg,message_type):
        self.parent = parent
        self.msg = msg
        self.message_type = message_type
        
        self.mainvbox = Gtk.Box.new(Gtk.Orientation.VERTICAL,1)

        
        self.infobar = Gtk.InfoBar()
        self.infobar.set_show_close_button(True)
        self.infobar.connect("response", self.hide__)
        
        self.label = Gtk.Label()
        self.label.props.label = self.msg
        self.mainvbox.append(self.label)
        self.infobar.add_child(self.mainvbox )
        self.infobar.set_message_type(self.message_type)
        #self.infobar.props.no_show_all = True
        
        self.parent.append(self.infobar)
        self.hide__()
        
    def show__(self):
        self.infobar.set_revealed(True)
        self.infobar.show()

    def hide__(self, infobar=None, respose_id=None):
        self.infobar.set_revealed(False)
        self.infobar.hide()
        
        
        
class FBDownloader(Gtk.ApplicationWindow):
    __gsignals__ = { "ongetlinksdone"     : (GObject.SignalFlags.RUN_LAST, None, (str,)),
                     "version"            : (GObject.SignalFlags.RUN_LAST, None, (str,str,str))
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("PySaveTube")
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.all_video_info = {}
        self.__all_video = {}
        self.config__ = get_metadata_info()
        
        self.__spinner = Gtk.Spinner()
        self.__spinner.props.margin_top = 5
        self.__spinner.props.margin_bottom = 5

        
        headerbar = Adw.HeaderBar()
        headerbar.set_decoration_layout(":close")
        #headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)
        
        mainvbox   = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        mainvbox.set_hexpand(True)
        mainvbox.set_vexpand(True)
        self.vbox  = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vbox.set_hexpand(True)
        self.vbox.set_vexpand(True)
        self.vbox2 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vbox3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        networkmanager     = Gio.NetworkMonitor.get_default()
        self.networkstatus = networkmanager.get_connectivity()
        self.statuspage    = Adw.StatusPage.new()
        

        
        self.stack1 = Gtk.Stack.new()
        self.stack1.set_hexpand(True)
        self.stack1.set_vexpand(True)
        self.stack1.set_transition_duration(200)
        self.stack1.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        
        self.stack1.add_titled(self.vbox,"vbox","Main")
        self.stack1.add_titled(self.vbox2,"vbox2","Youtube-dl")
        self.stack1.add_titled(self.vbox3,"vbox3","Network Status")
        self.stack1.connect("notify::visible-child",self.on_visible_child_changed)

        self.stack1.get_page(self.vbox).set_icon_name("open-menu-symbolic")
        self.stack1.get_page(self.vbox2).set_icon_name("software-update-available-symbolic")
        self.stack1.get_page(self.vbox3).set_icon_name("network-wireless-signal-excellent-symbolic")


        
        view_switcher_title = Adw.ViewSwitcherTitle.new()
        view_switcher_title.set_stack(self.stack1)
        view_switcher_title.set_policy(Adw.ViewSwitcherPolicy.WIDE)
        headerbar.set_title_widget(view_switcher_title)
        
        view_switcher_bar = Adw.ViewSwitcherBar.new()
        view_switcher_bar.set_stack(self.stack1)

        link_hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,5)
        link_hbox.props.margin_top = 5
        link_hbox.props.margin_bottom = 5
        link_hbox.props.margin_start = 5
        link_hbox.props.margin_end = 5


        
        link_label = Gtk.Label()
        link_label.props.label = _("Url")
        link_label.get_style_context().add_class("h1")
        
        self.pastebutton =  Gtk.Button.new_from_icon_name("edit-paste-symbolic")
        self.pastebutton.connect("clicked",self.on_paste_button_clicked)
        headerbar.pack_start(self.pastebutton)
        
        self.link_entry = Gtk.Entry()
        self.link_entry.set_hexpand(True)
        self.link_entry.props.placeholder_text = _("Enter  Video Url...")
        self.link_entry.set_input_purpose(Gtk.InputPurpose.URL)
        self.link_entry.set_has_frame(True)
        self.link_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"edit-clear-symbolic")
        self.link_entry.connect("icon_press",self.on_entry_icon_press)

        self.info_button = Gtk.Button()
        self.info_button.props.label = _("Get Info")
        self.info_button.connect("clicked",self.on_info_button_clicked)

        
        link_hbox.append(link_label)
        link_hbox.append(self.link_entry)
        link_hbox.append(self.info_button)
        
        
        self.infobar = MInfoBar(self.vbox,"",Gtk.MessageType.INFO)
        self.infobar2 = MInfoBarB(self.vbox,Gtk.MessageType.INFO)
        self.vbox.append(self.__spinner)
        self.vbox.append(link_hbox)
        
        self.statuspage.set_title(_("Network Status"))
        self.statuspage.set_hexpand(True)
        self.statuspage.set_vexpand(True)
        if self.networkstatus == Gio.NetworkConnectivity.FULL:
            self.statuspage.set_icon_name(NETWORKTR)
            self.statuspage.set_description(_("Network Connected."))
        else:
            self.statuspage.set_icon_name(NETWORKERROR)
            self.statuspage.set_description(_("Network Error."))
            self.infobar.label.props.label = _("Network Error.")
            self.infobar.show__()
        self.vbox3.append(self.statuspage)
        networkmanager.connect("network-changed",self.on_network_changed)
        
        self.installspinner = Gtk.Spinner()
        self.installspinner.props.margin_bottom = 5
        #self.installspinner.props.no_show_all = True
        self.check_youtube_dl_update_button = Gtk.Button()
        self.check_youtube_dl_update_button.props.label = _("Update Youtube-dl")
        self.connect("version",self.on_youtube_dl_version_check_done)
        self.check_youtube_dl_update_button.connect("clicked",self.t_check_if_youtube_dl_need_update)
        self.statuspage2  = Adw.StatusPage.new()
        self.statuspage2.set_hexpand(True)
        self.statuspage2.set_vexpand(True)
        self.check_for_update_infobar  = MInfoBar(self.vbox2,"",Gtk.MessageType.INFO)
        self.vbox2.append(self.statuspage2)
        self.vbox2.append(self.installspinner)
        self.statuspage2.set_title(_("Youtube-dl Status"))
        self.__isinstall = True
        self.installbutton = Gtk.Button()
        self.installbutton.props.label = _("Install Youtube-dl")
        self.installbutton.connect("clicked",self.on_install_clicked)
        if  not youtub_dl_exists:
            self.statuspage2.set_icon_name("face-sad-symbolic")
            self.statuspage2.set_description(_("Youtube-dl not found"))
            self.stack1.set_visible_child(self.vbox2)
            self.stack1.get_page(self.vbox2).set_needs_attention(True) 
            self.vbox.set_sensitive(False)
            self.vbox2.append(self.installbutton)
        else:
            self.statuspage2.set_icon_name("face-cool-symbolic")
            self.statuspage2.set_description(_("Version : ")+youtube_dl.version.__version__)
            self.vbox2.append(self.check_youtube_dl_update_button)

        flap = Adw.Flap.new()
        flap.set_content(self.stack1)
        flap.set_separator(Gtk.Separator())
        
        avavat_vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL,1)
        avavat_vbox.props.margin_top = 5
        avavat_vbox.props.margin_bottom = 5
        avavat_vbox.props.margin_start = 5
        avavat_vbox.props.margin_end = 5
        avavat_vbox.set_hexpand(False)
        avatar = Adw.Avatar()
        avatar.set_show_initials(True)
        avatar.set_size(150)
        avatar.set_text("About")
        
        label_avatar1 = Gtk.Label()
        label_avatar1.props.ellipsize = Pango.EllipsizeMode.END
        label_avatar1.set_justify(Gtk.Justification.CENTER)
        label_avatar1.get_style_context().add_class("h1")
        label_avatar1.props.label = "Pysavetube"
        
        label_avatar2 = Gtk.Label()
        label_avatar2.props.ellipsize = Pango.EllipsizeMode.END
        label_avatar2.set_justify(Gtk.Justification.CENTER)
        label_avatar2.get_style_context().add_class("h2")
        label_avatar2.props.label = "V 2.0\nLicense : GPLv3"
        
        linkbutton_avatar2 = Gtk.LinkButton.new_with_label("https://github.com/yucefsourani/pysavetube","WebSite")
        
        listbox = Gtk.ListBox.new()
        

        action_row = Adw.ExpanderRow.new()
        action_row.set_title(_("Login"))
        self.name_entry = Gtk.Entry.new()
        self.name_entry.props.placeholder_text = _("Username")
        self.name_entry.connect("notify::text",self.on_entry_changed,avatar,label_avatar1)
        self.name_entry.set_input_hints(Gtk.InputHints.NO_EMOJI | Gtk.InputHints.NO_SPELLCHECK )
        self.name_entry.set_input_purpose(Gtk.InputPurpose.EMAIL )
        self.name_entry.set_has_frame(True)
        self.name_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"edit-clear-symbolic")
        self.name_entry.connect("icon_press",self.on_entry_icon_press)
        
        self.password_entry = Gtk.Entry.new()
        self.password_entry.props.placeholder_text = _("Password")
        self.password_entry.set_input_hints(Gtk.InputHints.NO_EMOJI | Gtk.InputHints.NO_SPELLCHECK )
        self.password_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD  )
        self.password_entry.set_visibility(False)
        self.password_entry.set_has_frame(True)
        self.password_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"avatar-default-symbolic")
        self.password_entry.connect("icon_press",self.on_entry_show_hide_passoword_press)

        
        switch_label = Gtk.Label()
        switch_label.props.ellipsize = Pango.EllipsizeMode.END
        switch_label.props.label     = _("Use Password")
        use_password_switch_grid     = Gtk.Grid()
        self.use_password_switch     = Gtk.Switch()
        use_password_switch_grid.attach(self.use_password_switch,1,1,1,1)
        
        action_row.add(self.name_entry)
        action_row.add(self.password_entry)
        action_row.add(Gtk.Separator())
        action_row.add(switch_label)
        action_row.add(use_password_switch_grid)
        #listbox.add(action_row) # for later
        
        
        action_row2 = Adw.ExpanderRow.new()
        action_row2.set_title(_("Timeout"))
        global timeout_
        timeout_ = self.config__["timeout"]
        ad = Gtk.Adjustment.new(timeout_, 1, 60, 1, 0, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_hexpand(True)
        spinbutton.props.adjustment = ad
        spinbutton.connect("value_changed",self.on_spinbutton_changed)
        spin_grid = Gtk.Grid()
        spin_grid.attach(spinbutton,1,1,1,1)
        action_row2.add(spin_grid)
        listbox.append(action_row2)
        
        avavat_vbox.append(avatar)
        avavat_vbox.append(label_avatar1)
        avavat_vbox.append(label_avatar2)
        avavat_vbox.append(linkbutton_avatar2)
        avavat_vbox.append(listbox)
        flap.set_flap(avavat_vbox)
        flap.set_hexpand(True)
        flap.set_vexpand(True)

        view_switcher_title.connect("notify::title-visible",self.on_headerbar_squeezer_notify,view_switcher_bar)
        
        
        self.sw = Gtk.ScrolledWindow()
        self.sw.set_hexpand(True)
        self.sw.set_vexpand(True)
        self.listbox = Gtk.ListBox()
        self.listbox.set_hexpand(True)
        self.listbox.set_vexpand(True)
        self.listbox.set_show_separators(True)
        self.listbox.set_activate_on_single_click(True)
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE )
        self.vbox.append(self.sw)
        self.sw.set_child(self.listbox)
        
        mainvbox.append(flap)
        mainvbox.append(view_switcher_bar)
        self.set_child(mainvbox)
        

        self.connect("ongetlinksdone",self.on_get_links_done)

        for i in self.config__["current_links"]:
            self.make_listbox_row(i)
        
    def on_entry_show_hide_passoword_press(self, entry,icon_position,event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button.button==1:
            if entry.get_visibility():
                entry.set_visibility(False)
                entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"avatar-default-symbolic")
            else:
                entry.set_visibility(True)
                entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"user-not-tracked-symbolic")
        
    def on_visible_child_changed(self,stack,para):
        stack.get_page(stack.props.visible_child).set_needs_attention(False) 
        
    def get_links(self,url):
        result = ""
        self.all_video_info.setdefault(url,[])
        try:
            options = {"youtube_include_dash_manifest" : False}
            if self.use_password_switch.get_active():
                user_ = self.name_entry.get_text().strip()
                pass_ = self.password_entry.get_text().strip()
                if user_ and pass_:
                    options["username"] = user_
                    options["password"] = pass_
                elif pass_:
                    options["videopassword"] = pass_ 
            ydl = youtube_dl.YoutubeDL(options)
            with ydl:
                result__ = ydl.extract_info(
                    url,
                    download=False
                )

            if "formats" not in result__.keys():
                GLib.idle_add(self.infobar.label.set_label ,_("Playlist not supported"))
                GLib.idle_add(self.infobar.show__)
                GLib.idle_add(self.__spinner.stop)
                GLib.idle_add(self.__spinner.hide)
                GLib.idle_add(self.info_button.set_sensitive,True)
                return
            for i in result__["formats"]:
                if "format_note" in i.keys():
                    if i['format_note'] == 'tiny' :
                        continue
                rlt    = i["url"]
                req2   = request.Request(rlt,headers={"User-Agent":"Mozilla/5.0"})
                opurl2 = request.urlopen(req2,timeout=timeout_)          
                size   = int(opurl2.headers["Content-Length"])
                sizes  = round(int(opurl2.headers["Content-Length"])/1024/1024,2)
                self.all_video_info[url].append((result__["id"],
                                                 result__["title"],
                                                 result__["extractor"],
                                                 result__["thumbnail"],
                                                 rlt,
                                                 sizes,
                                                 size,
                                                 i["format_id"],
                                                 i["ext"],
                                                 i["format"],
                                                 url))
        except Exception as e :
            print(e)
            GLib.idle_add(self.__spinner.stop)
            GLib.idle_add(self.__spinner.hide)
            GLib.idle_add(self.info_button.set_sensitive,True)
            return 
            
        GLib.idle_add(self.info_button.set_sensitive,True)
        if  result__["extractor"]  in DROPED:
            GLib.idle_add(self.infobar.label.set_label ,_("Extractor not supported"))
            GLib.idle_add(self.infobar.show__)
            GLib.idle_add(self.__spinner.stop)
            GLib.idle_add(self.__spinner.hide)
            return


        GLib.idle_add(self.emit,"ongetlinksdone",url)

        
    def get_links_t(self,url):
        self.__spinner.show()
        self.__spinner.start()
        self.__spinner.queue_draw()
        while   GLib.MainContext.default().pending():
             GLib.MainContext.default().iteration()
        t = threading.Thread(target=self.get_links,args=(url,))
        t.setDaemon(True)
        t.start()
        
    def on_get_links_done(self,mainwindow,link):
        self.__spinner.stop()
        self.__spinner.hide()
        if link not in self.all_video_info.keys():
            return
        result = self.all_video_info[link]
        if not result:
            return
        self.config__["current_links"].append(result)
        change_metadata_info(self.config__)
        self.make_listbox_row(result)
        
    def on_load_image_finish(self,source_object, res, ggg):
        try:
            input_stream = source_object.read_finish(res)
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(input_stream,280, 200, True, None)
            ggg.set_from_pixbuf(pixbuf)
        except Exception as e:
            print(e)

        
    def make_listbox_row(self,result):
        if not result:
            return
        row = Gtk.ListBoxRow()
        row.props.margin_top = 5
        row.props.margin_bottom = 5
        row.props.margin_start = 5
        row.props.margin_end = 5
        v   = Gtk.Box.new(Gtk.Orientation.VERTICAL,5)
        v.set_margin_top(5)
        v.set_margin_bottom(5)
        v.set_margin_start(5)
        v.set_margin_end(5)
        h   = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,5)
        row.set_child(v)
        self.listbox.insert(row,0)
        label = Gtk.Label()
        label.set_margin_top(5)
        label.set_margin_bottom(5)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_selectable(True)
        label.props.label = result[-1][10]+"\n\n"+result[-1][1]
        label.props.ellipsize = Pango.EllipsizeMode.END
        v.append(label)
        v.append(h)
        progb = Gtk.ProgressBar()
        progb.set_hexpand(True)
        progb.set_vexpand(True)
        #progb.set_halign(Gtk.Align.CENTER)
        progb.set_show_text(True)
        progb.set_margin_bottom(10)
        progbhb = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,5)
        progbhb.append(progb)
        v.append(progbhb)
        h2 = Gtk.Box.new(Gtk.Orientation.HORIZONTAL,10)
        h2.set_hexpand(True)
        h2.set_vexpand(True)
        h2.set_halign(Gtk.Align.CENTER)
        v.append(h2)
        v1 = Gtk.Box.new(Gtk.Orientation.VERTICAL,5)
        v2 = Gtk.Box.new(Gtk.Orientation.VERTICAL,5)
        v3 = Gtk.Box.new(Gtk.Orientation.VERTICAL,5)
        h2.append(v2)
        h2.append(v3)
        #ggg = GstWidget(result[-1][4],self)
        #ggg = Gtk.Image()
        #url_ = result[-1][3]
        #if "ytimg" in url_:
        #    url_ = url_.split("?")[0]
        #file__ = Gio.File.new_for_uri(url_)
        #file__.read_async(1,None,self.on_load_image_finish,ggg)
        ggg = Gtk.Video.new_for_file(Gio.file_new_for_uri(result[-1][4]))
        media_s = ggg.get_media_stream()
        ggg.set_size_request(150,150)
        ggg.set_hexpand(True)
        ggg.set_vexpand(True)
        #ggg.set_halign(Gtk.Align.CENTER)
        self.__all_video.setdefault(result[-1][4] , media_s)
        
        if not win:
            v1.append(ggg)
        store = Gtk.ListStore(str,str,str,str,str,int,int,str,str,str,str)
        for i in result:
            iterr = store.append()
            for k in range(0,len(i)):
                store.set(iterr,k,i[k])

        combo = Gtk.ComboBox.new_with_model(store)
        renderer_text = Gtk.CellRendererText()
        renderer_text.props.ellipsize  = Pango.EllipsizeMode.END
        renderer_text.props.max_width_chars = 20
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 9)
        combo.set_active(len(store)-1)

        
        close_button = Gtk.Button()
        close_button.props.label = _("Remove Task")
        button = Gtk.Button()
        button.props.label = _("Download")
        cancel_button = Gtk.Button()
        cancel_button.props.label = _("Cancel")
        cancel_button.set_sensitive(False)
        v2.append(combo)
        v2.append(close_button)
        v3.append(button)
        v3.append(cancel_button)
        if not win:
            h.append(v1)

        button.connect("clicked",self.on_download,progb,store,combo,cancel_button,close_button)
        close_button.connect("clicked",self.on_close,row,result,)
        progb.hide()
        
    def on_close(self,button,row,result,force=False):
        if not force:
            self.infobar2.label.props.label = _("Are You Sure\nYou Want To Remove This Task?")
            self.infobar2.send_button = True
            self.infobar2.b.props.label = _("Remove")
            self.infobar2.row    = row
            self.infobar2.result = result
            self.infobar2.func   = self.on_close
            self.infobar2.show__()
            return
        if result[-1][4] in self.__all_video.keys():
            self.__all_video[result[-1][4]].set_playing(False)
            del self.__all_video[result[-1][4]]
        self.listbox.remove(row)
        self.config__["current_links"].remove(result)
        change_metadata_info(self.config__)

        
    def on_download(self,button,progressbar,store,combo,cancel_button,close_button):
        mode = "wb"
        if win:
            saveas_location = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),store[combo.get_active_iter()][1].replace("/"," ").replace("\\"," ")+store[combo.get_active_iter()][-2]+"."+store[combo.get_active_iter()][8])
        else:
            saveas_location = os.path.join(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),store[combo.get_active_iter()][1].replace("/"," ").replace("\\"," ")+store[combo.get_active_iter()][-2]+"."+store[combo.get_active_iter()][8])
            
        if  os.path.exists(saveas_location):
            if os.stat(saveas_location).st_size == int(store[combo.get_active_iter()][6]):
                progressbar.set_text(_("Already Exists"))
                progressbar.show()
                return
                
            mode = "ab"
        if win:
            t = DownloadFile(self,progressbar,button,store[combo.get_active_iter()][4],GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),store[combo.get_active_iter()][1].replace("/"," ").replace("\\"," ")+store[combo.get_active_iter()][-2]+"."+store[combo.get_active_iter()][8],store[combo.get_active_iter()][6],cancel_button,close_button,mode)
        else:
            t = DownloadFile(self,progressbar,button,store[combo.get_active_iter()][4],GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),store[combo.get_active_iter()][1].replace("/"," ").replace("\\"," ")+store[combo.get_active_iter()][-2]+"."+store[combo.get_active_iter()][8],store[combo.get_active_iter()][6],cancel_button,close_button,mode)
        t.setDaemon(True)
        cancel_button.connect("clicked",self.on_cancel_button_clicked,t)
        cancel_button.set_sensitive(True)
        t.start()
        
    def on_cancel_button_clicked(self,button,t):
        t.emit("break")
        button.set_sensitive(False)
        
    def on_info_button_clicked(self,button):
        url = self.link_entry.get_text().strip()
        if not url:
            return 
        if any( [True for i in self.config__["current_links"] if i if  url in i[-1][10] ]):
            return
            
        button.set_sensitive(False)
        self.get_links_t(url)
        
    def on_entry_icon_press(self,entry, icon_pos):
        entry.set_text("")
        
    def on_network_changed(self,networkmanager, network_available):
        networkstatus   = networkmanager.get_connectivity()
        if networkstatus == Gio.NetworkConnectivity.FULL:
            self.statuspage.set_icon_name(NETWORKTR)
            self.statuspage.set_description(_("Network Connected."))
            self.infobar.label.props.label = _("Network Connected.")
            self.infobar.show__()
        else:
            self.statuspage.set_icon_name(NETWORKERROR)
            self.statuspage.set_description(_("Network Error."))
            self.networkstatus = networkstatus
            self.infobar.label.props.label = _("Network Error.")
            self.infobar.show__()
        self.stack1.get_page(self.vbox3).set_needs_attention(True) 
            

    def on_clipboard_read_text(self,clipboard,result,data):
        text = ""
        try:
            text = clipboard.read_text_finish(result)
        except:
            pass
        if text :
            self.link_entry.set_text(text)
            
    def on_paste_button_clicked(self,button):
        clipboard = self.get_clipboard()
        clipboard.read_text_async(None,self.on_clipboard_read_text,None)
            
    def on_spinbutton_changed(self,spinbutton):
        global timeout_
        timeout_ = spinbutton.get_value_as_int()

        
    def on_entry_changed(self,entry,prop,avatar,avatar_label):
        text = entry.get_text().strip()
        avatar.set_text(text)
        avatar_label.set_label(text)
        
    def on_headerbar_squeezer_notify(self, view_switcher_title, prop,view_switcher_bar):
        view_switcher_bar.set_reveal( view_switcher_title.props.title_visible)


    def on_install_clicked(self,installbutton):
        threading.Thread(target=self.install_update_youtube_dl).start()


    def install_update_youtube_dl(self):
        GLib.idle_add(self.installbutton.set_sensitive,False)
        GLib.idle_add(self.installspinner.show)
        GLib.idle_add(self.installspinner.start)
        try:
            link  = "https://ytdl-org.github.io/youtube-dl/update/versions.json"
            url   = request.Request(link,headers=HEADERS)
            opurl = request.urlopen(url,timeout=timeout_)
            json_dict = json.loads(opurl.read().decode('utf-8'))
            opurl.close()
            
            last_version = json_dict["latest"]
            tar_link     = json_dict["versions"][last_version]["tar"][0]
            url   = request.Request(tar_link,headers=HEADERS)
            opurl = request.urlopen(url,timeout=timeout_)
            tarfilename = os.path.basename(tar_link)
            with tempfile.TemporaryDirectory() as tmpdirname:
                save_as = os.path.join(tmpdirname,tarfilename)
                with open(save_as, 'wb') as op:
                    op.write(opurl.read())
                tar = tarfile.open(save_as)
                tar.extractall(path=YOUTYBEDLDIR)
                tar.close()
            global youtube_dl
            global youtub_dl_exists
            module_path = glob.glob(YOUTYBEDLDIR+"/youtube-dl/youtube_dl/__init__.py")
            if len(module_path)>0:
                module_path = module_path[0]
                try:
                    youtube_dl = load_module(module_path)
                    youtub_dl_exists = True
                except:
                    youtub_dl_exists = False
            else:
                youtub_dl_exists = False
        except Exception as e:
            print(e)
            GLib.idle_add(self.emit,"version","e","","")
            GLib.idle_add(self.installspinner.stop)
            GLib.idle_add(self.installspinner.hide)
            GLib.idle_add(self.check_youtube_dl_update_button.set_sensitive,True)
            GLib.idle_add(self.installbutton.set_sensitive,True)
            return 
        finally:
            try:
                opurl.close()
            except:
                pass
        GLib.idle_add(self.statuspage2.set_icon_name,"face-cool-symbolic")
        GLib.idle_add(self.installspinner.stop)
        GLib.idle_add(self.installspinner.hide)
        if self.__isinstall:
            GLib.idle_add(self.statuspage2.set_description,(_("Version : ")+youtube_dl.version.__version__))
            GLib.idle_add(self.vbox2.remove,self.installbutton)
            GLib.idle_add(self.vbox2.append,self.check_youtube_dl_update_button)
            GLib.idle_add(self.vbox.set_sensitive,True)
            GLib.idle_add(self.check_youtube_dl_update_button.set_sensitive,True)
        else:
            GLib.idle_add(self.statuspage2.set_description,(_("New Version : ")+last_version))
            GLib.idle_add(self.check_for_update_infobar.label.set_label ,"Please Restart Pysavetube")
            GLib.idle_add(self.check_for_update_infobar.show__)

        self.__isinstall = True
        GLib.idle_add(self.installbutton.set_sensitive,True)
        #GLib.idle_add(self.infobar.hide__)
        
    def on_youtube_dl_version_check_done(self,parent,result,remote_version,local_version):
        if result == "e":
            if self.__isinstall:
                msg = _('ERROR:\ncan\'t install youtube-dl.\nPlease try again later.')
            else:
                msg = _('ERROR:\ncan\'t find the lastes version.\nPlease try again later.')
        elif result == "n":
            msg = _('youtube-dl is up-to-date;')+'\n' + local_version 
        else:
            msg = _('youtube-dl need update to:')+'\n' + remote_version
            self.__isinstall = False
            GLib.idle_add(self.statuspage2.set_icon_name,"face-surprise-symbolic")
            self.installbutton.emit("clicked")
            
        self.check_for_update_infobar.label.props.label = msg
        GLib.idle_add(self.check_for_update_infobar.show__)
        
        
    def t_check_if_youtube_dl_need_update(self,button=None):
        self.check_for_update_infobar.label.props.label = _("Searching for update...")
        self.check_for_update_infobar.show__()
        threading.Thread(target=self.check_if_youtube_dl_need_update).start()
        
    def check_if_youtube_dl_need_update(self):
        self.__isinstall = False
        GLib.idle_add(self.check_youtube_dl_update_button.set_sensitive,False)
        GLib.idle_add(self.installspinner.show)
        GLib.idle_add(self.installspinner.start)
        try:
            link  = "https://yt-dl.org/update/LATEST_VERSION"
            url   = request.Request(link,headers=HEADERS)
            opurl = request.urlopen(url,timeout=timeout_)
            remote_version = opurl.read().decode('utf-8').strip()
            local_version = youtube_dl.version.__version__
        except Exception as e:
            print(e)
            GLib.idle_add(self.emit,"version","e","","")
            GLib.idle_add(self.installspinner.hide)
            GLib.idle_add(self.installspinner.stop)
            GLib.idle_add(self.check_youtube_dl_update_button.set_sensitive,True)
            return 
        finally:
            try:
                opurl.close()
            except:
                pass
        GLib.idle_add(self.installspinner.hide)
        GLib.idle_add(self.installspinner.stop)
        if remote_version != local_version:
            GLib.idle_add(self.emit,"version","y",remote_version,local_version)
        else:
            GLib.idle_add(self.check_youtube_dl_update_button.set_sensitive,True)
            GLib.idle_add(self.emit,"version","n",remote_version,local_version)
                
class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id=appid,
                         flags=Gio.ApplicationFlags(0),
                         **kwargs)
        self.window = None
        
    def do_startup(self):
        Gtk.Application.do_startup(self)
        
    def do_activate(self):
        if not self.window:
            self.window = FBDownloader(application=self, title=appwindowtitle)
            self.window.connect("close_request",self.on_quit)
        self.window.present()

    def on_quit(self, action=None, param=None,force=False,b=None):
        if not force:
            if threading.active_count()>1:
                self.window.infobar2.label.props.label = _("Tasks Running In Background,\nAre You Sure You Want To Exit?")
                self.window.infobar2.b.props.label = _("Exit")
                self.window.infobar2.send_button = False
                self.window.infobar2.row=action
                self.window.infobar2.result=param
                self.window.infobar2.func=self.on_quit
                self.window.infobar2.show__()
                return True
        if win:
            self.window.config__["current_save_location"] = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS).replace("\\","/")
        else:
            self.window.config__["current_save_location"] = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS)
        
        self.window.config__["timeout"] = timeout_
        change_metadata_info(self.window.config__)
        
        self.quit()




if __name__ == "__main__":
    app = Application()
    app.run(sys.argv)

