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
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gdk, Gio, GLib, Gst, GObject, Pango, GdkPixbuf
gi.require_version('Handy', '1')
from gi.repository import Handy
import sys
import threading
import urllib.request as request
import re
import os
import sys
import subprocess
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

win =  sys.platform.startswith('win')
skipnetworkstatus =  False
if win:
    os.environ['GDK_WIN32_LAYERED'] = "0"
    default_metadata = """{{"current_links"           : [],"current_save_location"   : "{}","timeout" : 10}}
    """.format(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS).replace("\\","/"))
    import locale
    if os.getenv('LANG') is None:
        lang, enc = locale.getdefaultlocale()
        os.environ['LANG'] = lang

fix_certifi()
Gst.init(None)
Gst.init_check(None)

gettext.install('pysavetube', localedir=get_correct_path('locale'))

authors_         = ["Youssef Sourani <youssef.m.sourani@gmail.com>"]
version_         = "1.0"
copyright_       = "Copyright © 2021 Youssef Sourani"
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
Handy.init()

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

class GstWidget(Gtk.EventBox):
    def __init__(self, link,parent):
        super().__init__()
        self.link = link
        self.parent= parent
        self.set_size_request(280, 200)

        
        self.overlay = Gtk.Overlay()
        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK  | Gdk.EventMask.LEAVE_NOTIFY_MASK  )
        self.add(self.overlay)
        self.connect("leave-notify-event",self.on_leave)
        self.connect("enter-notify-event",self.on_enter)
        
        pix1 = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(get_correct_path("pysavetube-data/images"),"play.png"),32,32,True)
        self.playi = Gtk.Image.new_from_pixbuf(pix1 )
        self.play  = Gtk.EventBox()
        self.play.add(self.playi)
        self.play .set_halign(Gtk.Align.CENTER)
        self.play .set_valign(Gtk.Align.CENTER)
        self.play.add_events(Gdk.EventMask.BUTTON_PRESS_MASK )
        self.play.connect("button-press-event",self.on_play)

        pix2 = GdkPixbuf.Pixbuf.new_from_file_at_scale(os.path.join(get_correct_path("pysavetube-data/images"),"stop.svg"),32,32,True)
        self.stopi = Gtk.Image.new_from_pixbuf(pix2)
        self.stop  = Gtk.EventBox()
        self.stop.add(self.stopi)
        self.stop .set_halign(Gtk.Align.CENTER)
        self.stop .set_valign(Gtk.Align.CENTER)
        self.stop.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.stop.connect("button-press-event",self.on_stop)
        
        self.activate_image = self.play 
        
        self.connect('realize', self.on_realize)
        
    def on_play(self,image,event):
        playerState = self.playbin.get_state(Gst.SECOND).state
        if playerState !=  Gst.State.PLAYING:
            self.playbin.set_state(Gst.State.PLAYING)
            self.activate_image  = self.stop
            self.overlay.add_overlay(self.stop)
            self.stop.show_all()
            
    def on_stop(self,image,event):
        playerState = self.playbin.get_state(Gst.SECOND).state
        if playerState != Gst.State.PAUSED:
            self.playbin.set_state(Gst.State.PAUSED)
            self.activate_image  = self.play
            self.overlay.add_overlay(self.play)
            self.play.show_all()

    def on_leave(self,box,event):
        self.overlay.remove(self.activate_image)
        self.play.hide()
        self.stop.hide()
        
    def on_enter(self,box,event):
        playerState = self.playbin.get_state(Gst.SECOND).state
        if playerState <= Gst.State.PAUSED:
            self.activate_image  = self.play
            self.overlay.add_overlay(self.play)
            self.play.show_all()
        elif playerState is Gst.State.PLAYING:
            self.activate_image  = self.stop
            self.overlay.add_overlay(self.stop)
            self.stop.show_all()
                   
    def on_realize(self, widget):
        gtksink   = Gst.ElementFactory.make('gtksink')
        self.overlay.add(gtksink.props.widget)
        gtksink.props.widget.show()

        
        self.playbin   = Gst.ElementFactory.make("playbin")
        self.playbin.set_property('uri', self.link)
        self.playbin.set_property('force-aspect-ratio', True)
        self.playbin.set_property('video-sink',gtksink)

        self.__bus1 = self.playbin.get_bus()
        self.__bus1.add_signal_watch()
        self.__bus1.connect("message", self.__on_message)

    def __on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.playbin.set_state(Gst.State.NULL)
            self.activate_image  = self.play
            self.overlay.add_overlay(self.play)
            self.play.show_all()
        elif t == Gst.MessageType.ERROR:
            self.playbin.set_state(Gst.State.NULL)
            self.activate_image  = self.play
            self.overlay.add_overlay(self.play)
            self.play.show_all()


class DownloadFile(GObject.Object,threading.Thread):
    __gsignals__ = { "break"     : (GObject.SignalFlags.RUN_LAST, None, ())
    }
    
    def __init__(self,parent,progressbar,button,link,location,format_,username=None,
                 password=None,videopassword=None,playlist=None,outtmpl="%(id)s.%(format)s.%(title)s.%(ext)s",
                 cancel_button=None,close_button=None,
                 ignoreerrors=False,nooverwrites=True,skip_download=True,continue_dl=True,subtitle=False):
        GObject.Object.__init__(self)
        threading.Thread.__init__(self)
        self.parent        = parent
        self.progressbar   = progressbar
        self.button        = button
        self.link          = link
        self.format_       = format_
        self.username      = username
        self.password      = password 
        self.videopassword = videopassword
        self.playlist      = playlist
        self.outtmpl       = outtmpl
        self.location      = location
        self.break_        = False
        self.cancel_button = cancel_button
        self.close_button  = close_button
        self.ignoreerrors  = ignoreerrors
        self.nooverwrites  = nooverwrites
        self.skip_download = skip_download
        self.continue_dl   = continue_dl
        self.subtitle      = subtitle
        self.connect("break",self.on_break)
        self.canceled = False


        

    def on_break(self,s):
        self.break_ = True        
            
    def run(self):
        ydl_opts      = {}
        self.break_ = False
        GLib.idle_add(self.progressbar.show)
        GLib.idle_add(self.button.set_sensitive,False)
        GLib.idle_add(self.close_button.set_sensitive,False)
        
        
        ydl_opts["format"]            = self.format_
        if self.username:
            ydl_opts["username"]          = self.username
        if self.password:
            ydl_opts["password"]          = self.password
        if self.videopassword:
            ydl_opts["videopassword"]     = self.videopassword
            
        if self.subtitle:
            ydl_opts["subtitleslangs"]     = [self.subtitle.split("-")[0]]
            ydl_opts["subtitlesformat"]    = self.subtitle.split("-")[1]
            ydl_opts["writesubtitles"]     = True
            ydl_opts["writeautomaticsub"]  = True
            self.outtmpl = os.path.join(self.location,self.subtitle+"_"+self.outtmpl)
        else:
            self.outtmpl = os.path.join(self.location,self.outtmpl)
            
        
        ydl_opts["socket_timeout"]    = timeout_
        ydl_opts["ignoreerrors"]      = self.ignoreerrors
        ydl_opts["nooverwrites"]      = self.nooverwrites
        ydl_opts["continue_dl"]       = self.continue_dl
        ydl_opts["progress_hooks"]    = []
        ydl_opts["progress_hooks"].append(self.my_hook)
        ydl_opts["outtmpl"]           = self.outtmpl 
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link])
        except Exception as e:
            GLib.idle_add(self.progressbar.set_fraction,0.0)
            if self.canceled:
                GLib.idle_add(self.progressbar.set_text,_("Canceled!"))
            else:
                GLib.idle_add(self.progressbar.set_text,_("Fail"))
            GLib.idle_add(self.button.set_sensitive,True)
            GLib.idle_add(self.close_button.set_sensitive,True)
            GLib.idle_add(self.cancel_button.set_sensitive,False)
            print(e)
            
    def my_hook(self,d):
        if self.break_:
            self.canceled = True
            GLib.idle_add(self.progressbar.set_text,_("Canceled!"))
            GLib.idle_add(self.progressbar.set_fraction,0.0)
            GLib.idle_add(self.button.set_sensitive,True)
            GLib.idle_add(self.close_button.set_sensitive,True)
            GLib.idle_add(self.cancel_button.set_sensitive,False)
            raise Exception('Canceled!')
        status  = d["status"] 
        if status == 'finished':
            GLib.idle_add(self.progressbar.set_fraction,0.0)
            GLib.idle_add(self.progressbar.set_text,_("Done"))
            GLib.idle_add(self.button.set_sensitive,True)
            GLib.idle_add(self.close_button.set_sensitive,True)
            GLib.idle_add(self.cancel_button.set_sensitive,False)
            return True
        elif status == "error":
            if self.canceled:
                GLib.idle_add(self.progressbar.set_text,_("Canceled!"))
            else:
                GLib.idle_add(self.progressbar.set_text,_("Fail"))
            GLib.idle_add(self.progressbar.set_fraction,0.0)
            GLib.idle_add(self.button.set_sensitive,True)
            GLib.idle_add(self.close_button.set_sensitive,True)
            GLib.idle_add(self.cancel_button.set_sensitive,False)
            return True
        _percent_str      = d["_percent_str"]
        _speed_str        = d["_speed_str"]
        _eta_str          = d["_eta_str"]
        filename          = d["filename"]
        tmpfilename       = d["tmpfilename"]
        total_bytes       = d["total_bytes"]
        downloaded_bytes  = d["downloaded_bytes"]
        count = int((downloaded_bytes*100)//total_bytes)
        fraction = count/100
        GLib.idle_add(self.progressbar.set_fraction,fraction)
        GLib.idle_add(self.progressbar.set_text,_percent_str+" "+str(downloaded_bytes)+"/"+str(total_bytes)+" B")



class MInfoBarB():
    def __init__(self,parent,message_type,row=None,result=None,func=None):
        self.parent       = parent
        self.message_type = message_type
        self.row          = row
        self.result       = result
        self.func         = func
        self.send_button  = True

        
        self.mainhbox = Gtk.HBox()
        self.mainhbox.props.spacing = 10
        
        self.infobar = Gtk.InfoBar()
        self.infobar.set_show_close_button(True)
        self.infobar.connect("response", self.hide__)
        
        self.label = Gtk.Label()
        self.label.props.label = ""
        self.content = self.infobar.get_content_area()
        self.b = Gtk.Button()
        self.b.props.label = ""
        self.b.connect("clicked",self.on_b_clicked)
        self.mainhbox.pack_start(self.label,False,False,0)
        self.mainhbox.pack_start(self.b,False,False,0)
        self.content.add(self.mainhbox )
        self.infobar.set_message_type(self.message_type)
        self.infobar.props.no_show_all = True
        
        self.parent.add(self.infobar)

    def on_b_clicked(self,button):
        if self.send_button:
            self.func(button,self.row,self.result,force=True)
        else:
            self.func(self.row,self.result,force=True)
        self.infobar.hide()
        
    def show__(self):
        self.content.show_all()
        self.infobar.show()

    def hide__(self, infobar=None, respose_id=None):
        self.infobar.hide()
        
class MInfoBar():
    def __init__(self,parent,msg,message_type):
        self.parent = parent
        self.msg = msg
        self.message_type = message_type
        
        self.mainvbox = Gtk.VBox()
        self.mainvbox.props.spacing = 10
        
        self.infobar = Gtk.InfoBar()
        self.infobar.set_show_close_button(True)
        self.infobar.connect("response", self.hide__)
        
        self.label = Gtk.Label()
        self.label.props.label = self.msg
        self.content = self.infobar.get_content_area()
        self.mainvbox.pack_start(self.label,False,False,0)
        self.content.add(self.mainvbox )
        self.infobar.set_message_type(self.message_type)
        self.infobar.props.no_show_all = True
        
        self.parent.add(self.infobar)
        
    def show__(self):
        self.content.show_all()
        self.infobar.show()

    def hide__(self, infobar=None, respose_id=None):
        self.infobar.hide()
        
        
        
class FBDownloader(Gtk.ApplicationWindow):
    __gsignals__ = { "ongetlinksdone"     : (GObject.SignalFlags.RUN_LAST, None, (str,)),
                     "version"            : (GObject.SignalFlags.RUN_LAST, None, (str,str,str))
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if icon_:
            self.set_icon(GdkPixbuf.Pixbuf.new_from_file(icon_))
        self.set_title("PySaveTube")
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        self.all_video_info = {}
        self.config__ = get_metadata_info()
        
        self.__spinner = Gtk.Spinner()
        self.__spinner.props.no_show_all = True
        
        headerbar = Handy.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)
        
        mainvbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vbox     = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vbox.props.margin = 18
        self.vbox.props.spacing = 18
        self.vbox2      = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.vbox3 = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        if not win or skipnetworkstatus:
            networkmanager     = Gio.NetworkMonitor.get_default()
            self.networkstatus = networkmanager.get_connectivity()
            self.statuspage    = Handy.StatusPage.new()
        

        
        self.stack1 = Gtk.Stack.new()
        self.stack1.set_hexpand(True)
        self.stack1.set_vexpand(True)
        self.stack1.set_transition_duration(200)
        self.stack1.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        
        self.stack1.add_titled(self.vbox,"vbox","Main")
        self.stack1.add_titled(self.vbox2,"vbox2","Youtube-dl")
        if not win or skipnetworkstatus:
            self.stack1.add_titled(self.vbox3,"vbox3","Network Status")
        self.stack1.connect("notify::visible-child",self.on_visible_child_changed)

        self.stack1.child_set_property(self.vbox, 'icon-name', 'open-menu-symbolic')
        self.stack1.child_set_property(self.vbox2, 'icon-name', 'software-update-available-symbolic')
        if not win or skipnetworkstatus:
            self.stack1.child_set_property(self.vbox3, 'icon-name', 'network-wireless-signal-excellent-symbolic')

        
        view_switcher_title = Handy.ViewSwitcherTitle.new()
        view_switcher_title.set_stack(self.stack1)
        view_switcher_title.set_policy(Handy.ViewSwitcherPolicy.WIDE)
        headerbar.set_custom_title(view_switcher_title)
        
        view_switcher_bar = Handy.ViewSwitcherBar.new()
        view_switcher_bar.set_stack(self.stack1)

        link_hbox = Gtk.HBox()
        link_hbox.props.spacing = 5
        link_hbox.props.margin  = 5
        
        link_label = Gtk.Label()
        link_label.props.label = _("Url")
        link_label.get_style_context().add_class("h1")
        
        self.pastebutton = Gtk.Button.new_from_icon_name("edit-paste-symbolic", Gtk.IconSize.MENU)
        self.pastebutton.props.tooltip_text = "Paste URL"
        self.pastebutton.connect("clicked",self.on_paste_button_clicked)
        headerbar.pack_start(self.pastebutton)
        
        self.link_entry = Gtk.Entry()
        self.link_entry.props.placeholder_text = _("Enter  Video Url...")
        self.link_entry.set_input_purpose(Gtk.InputPurpose.URL)
        self.link_entry.set_has_frame(True)
        self.link_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"edit-clear-symbolic")
        self.link_entry.connect("icon_press",self.on_entry_icon_press)

        self.info_button = Gtk.Button()
        self.info_button.props.label = _("Get Info")
        self.info_button.connect("clicked",self.on_info_button_clicked)

        
        link_hbox.pack_start(link_label,False,False,0)
        link_hbox.pack_start(self.link_entry,True,True,0)
        link_hbox.pack_start(self.info_button,False,False,0)
        
        
        self.infobar = MInfoBar(self.vbox,"",Gtk.MessageType.INFO)
        self.infobar2 = MInfoBarB(self.vbox,Gtk.MessageType.INFO)
        self.vbox.pack_start(self.__spinner,False,False,5)
        self.vbox.pack_start(link_hbox,False,False,0)
        
        if not win or skipnetworkstatus:
            self.statuspage.set_title(_("Network Status"))
            if self.networkstatus == Gio.NetworkConnectivity.FULL:
                self.statuspage.set_icon_name(NETWORKTR)
                self.statuspage.set_description(_("Network Connected."))
            else:
                self.statuspage.set_icon_name(NETWORKERROR)
                self.statuspage.set_description(_("Network Error."))
                self.infobar.label.props.label = _("Network Error.")
                self.infobar.show__()
            self.vbox3.add(self.statuspage)
            networkmanager.connect("network-changed",self.on_network_changed)
        
        self.installspinner = Gtk.Spinner()
        self.installspinner.props.no_show_all = True
        self.check_youtube_dl_update_button = Gtk.Button()
        self.check_youtube_dl_update_button.get_style_context().add_class("suggested-action")
        self.check_youtube_dl_update_button.props.label = _("Update Youtube-dl")
        self.connect("version",self.on_youtube_dl_version_check_done)
        self.check_youtube_dl_update_button.connect("clicked",self.t_check_if_youtube_dl_need_update)
        self.statuspage2  = Handy.StatusPage.new()
        self.check_for_update_infobar  = MInfoBar(self.vbox2,"",Gtk.MessageType.INFO)
        self.vbox2.pack_start(self.statuspage2,True,True,0)
        self.vbox2.pack_start(self.installspinner,False,False,0)
        self.statuspage2.set_title(_("Youtube-dl Status"))
        self.__isinstall = True
        self.installbutton = Gtk.Button()
        self.installbutton.get_style_context().add_class("suggested-action")
        self.installbutton.props.label = _("Install Youtube-dl")
        self.installbutton.connect("clicked",self.on_install_clicked)
        if  not youtub_dl_exists:
            self.statuspage2.set_icon_name("face-sad-symbolic")
            self.statuspage2.set_description(_("Youtube-dl not found"))
            self.vbox2.show_all()
            self.stack1.set_visible_child(self.vbox2)
            self.stack1.child_set_property(self.vbox2, 'needs-attention', True)
            self.vbox.set_sensitive(False)
            self.vbox2.pack_start(self.installbutton,False,False,0)
        else:
            self.statuspage2.set_icon_name("face-cool-symbolic")
            self.statuspage2.set_description(_("Version : ")+youtube_dl.version.__version__)
            self.vbox2.pack_start(self.check_youtube_dl_update_button,False,False,0)

        flap = Handy.Flap.new()
        flap.set_content(self.stack1)
        flap.set_separator(Gtk.Separator())
        
        avatar_sw = Gtk.ScrolledWindow()
        avatar_sw.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC )
        avavat_vbox = Gtk.VBox()
        avavat_vbox.set_hexpand(False)
        avavat_vbox.set_vexpand(True)
        avatar = Handy.Avatar()
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
        label_avatar2.props.label = "V 1.0\nLicense : GPLv3"

        label_avatar3 = Gtk.Label()
        label_avatar3.props.ellipsize = Pango.EllipsizeMode.END
        label_avatar3.set_justify(Gtk.Justification.CENTER)
        label_avatar3.get_style_context().add_class("h3")
        label_avatar3.props.label = copyright_
        
        
        linkbutton_avatar2 = Gtk.LinkButton.new_with_label("https://github.com/yucefsourani/pysavetube","WebSite")
        
        listbox = Gtk.ListBox.new()
        
        action_row = Handy.ExpanderRow.new()
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

        self.video_pass_entry = Gtk.Entry.new()
        self.video_pass_entry.props.placeholder_text = _("Video Password")
        self.video_pass_entry.set_input_hints(Gtk.InputHints.NO_EMOJI | Gtk.InputHints.NO_SPELLCHECK )
        self.video_pass_entry.set_input_purpose(Gtk.InputPurpose.PASSWORD  )
        self.video_pass_entry.set_visibility(False)
        self.video_pass_entry.set_has_frame(True)
        self.video_pass_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY ,"avatar-default-symbolic")
        self.video_pass_entry.connect("icon_press",self.on_entry_show_hide_passoword_press)
        
        switch_label = Gtk.Label()
        switch_label.props.ellipsize = Pango.EllipsizeMode.END
        switch_label.props.label     = _("Use Password")
        use_password_switch_grid     = Gtk.Grid()
        self.use_password_switch     = Gtk.Switch()
        use_password_switch_grid.add(self.use_password_switch)
        

        
        
        action_row2 = Handy.ExpanderRow.new()
        action_row2.set_title(_("Timeout"))
        global timeout_
        timeout_ = self.config__["timeout"]
        ad = Gtk.Adjustment.new(timeout_, 1, 60, 1, 0, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_hexpand(True)
        spinbutton.props.adjustment = ad
        spinbutton.connect("value_changed",self.on_spinbutton_changed)
        spin_grid = Gtk.Grid()
        spin_grid.add(spinbutton)
        action_row2.add(spin_grid)
        listbox.add(action_row2)

        action_row.add(self.name_entry)
        action_row.add(self.password_entry)
        action_row.add(self.video_pass_entry)
        action_row.add(Gtk.Separator())
        action_row.add(switch_label)
        action_row.add(use_password_switch_grid)
        listbox.add(action_row) 
        
        avavat_vbox.pack_start(avatar,False,False,10)
        avavat_vbox.pack_start(label_avatar1,False,False,10)
        avavat_vbox.pack_start(label_avatar2,False,False,10)
        avavat_vbox.pack_start(label_avatar3,False,False,10)
        avavat_vbox.pack_start(linkbutton_avatar2,False,False,10)
        avavat_vbox.pack_start(listbox,False,False,0)
        avatar_sw.add(avavat_vbox)
        flap.set_flap(avatar_sw)

        view_switcher_title.connect("notify::title-visible",self.on_headerbar_squeezer_notify,view_switcher_bar)
        
        
        self.sw = Gtk.ScrolledWindow()
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.BROWSE )
        self.vbox.pack_start(self.sw,True,True,0)
        self.sw.add(self.listbox)
        
        mainvbox.add(flap)
        mainvbox.add(view_switcher_bar)
        self.add(mainvbox)
        
    
        self.show_all()
        self.connect("ongetlinksdone",self.on_get_links_done)

        for i in self.config__["current_links"]:
            url = i[0][4]
            self.all_video_info.setdefault(url,[])
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
        stack.child_set_property(stack.props.visible_child, 'needs-attention', False)
        
    def get_links(self,url):
        result = ""
        try:
            options = {"youtube_include_dash_manifest" : False , "socket_timeout" : timeout_}
            if self.use_password_switch.get_active():
                user_ = self.name_entry.get_text().strip()
                pass_ = self.password_entry.get_text().strip()
                video_pass = self.video_pass_entry.get_text().strip()
                if user_ and pass_:
                    options["username"] = user_
                    options["password"] = pass_
                if video_pass:
                    options["videopassword"] = video_pass

            ydl = youtube_dl.YoutubeDL(options)
            with ydl:
                result__ = ydl.extract_info(
                    url,
                    download=False
                )

            if "formats"  not in result__.keys():

                if "entries" in result__.keys():
                    for video_info in result__["entries"][::-1]:
                        rlt      = video_info["webpage_url"]
                        if rlt not in self.all_video_info.keys():
                            self.all_video_info.setdefault(rlt,[])
                        else:
                            continue
                        for i in video_info["formats"]:
                            if "format_note" in i.keys():
                                if i['format_note'] == 'tiny' :
                                    continue
                            if "subtitles" in video_info.keys():
                                subtitles  = video_info["subtitles"]
                            else:
                                subtitles  = {}
                            if  "thumbnails" in video_info.keys():
                                thumbnails = video_info["thumbnails"]
                            else:
                                thumbnails = []
                            sizes  = 0
                            size   = 0
                            self.all_video_info[rlt].append((video_info["id"],
                                                                 video_info["title"]+"\n\n<span foreground=\"green\">Playlist : {}</span>".format(video_info["playlist_title"])+"\n<span foreground=\"green\">({}/{})</span>".format(video_info["playlist_index"],video_info["n_entries"]),
                                                                 video_info["extractor"],
                                                                 video_info["thumbnail"],
                                                                 rlt,
                                                                 sizes,
                                                                 size,
                                                                 i["format_id"],
                                                                 i["ext"],
                                                                 i["format"],
                                                                 rlt,
                                                                 subtitles,
                                                                 thumbnails))
                                            
                                    
                            if  result__["extractor"]  in DROPED:
                                GLib.idle_add(self.__spinner.stop)
                                GLib.idle_add(self.__spinner.hide)
                                GLib.idle_add(self.info_button.set_sensitive,True)
                                GLib.idle_add(self.infobar.label.set_label ,_("Extractor not supported"))
                                GLib.idle_add(self.infobar.show__)
                                del self.all_video_info[rlt]
                                return
                        GLib.idle_add(self.emit,"ongetlinksdone",rlt)
                    GLib.idle_add(self.__spinner.stop)
                    GLib.idle_add(self.__spinner.hide)
                    GLib.idle_add(self.info_button.set_sensitive,True)
                    return
                else:
                    GLib.idle_add(self.infobar.label.set_label ,_("Task not supported"))
                    GLib.idle_add(self.infobar.show__)
                    GLib.idle_add(self.__spinner.stop)
                    GLib.idle_add(self.__spinner.hide)
                    GLib.idle_add(self.info_button.set_sensitive,True)
                    return
                
            else:
                self.all_video_info.setdefault(url,[])
                for i in result__["formats"]:
                    if "format_note" in i.keys():
                        if i['format_note'] == 'tiny' :
                            continue
                    if "subtitles" in result__.keys():
                        subtitles  = result__["subtitles"]
                    else:
                        subtitles  = {}
                    if  "thumbnails" in result__.keys():
                        thumbnails = result__["thumbnails"]
                    else:
                        thumbnails = []
                    rlt    = i["url"]
                    sizes = 0
                    size  = 0
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
                                                     url,
                                                     subtitles,
                                                     thumbnails))
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
            del self.all_video_info[url]
            return 
        GLib.idle_add(self.emit,"ongetlinksdone",url)

        
    def get_links_t(self,url):
        self.__spinner.show()
        self.__spinner.start()
        self.__spinner.queue_draw()
        while Gtk.events_pending():
            Gtk.main_iteration()
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
        v   = Gtk.VBox()
        v.props.spacing = 5
        v.set_margin_bottom(30)
        h   = Gtk.HBox()
        h.set_margin_start(5)
        h.set_margin_end(5)
        h.set_margin_top(5)
        h.set_margin_bottom(5)
        h.props.spacing = 5
        row.add(v)
        self.listbox.insert(row,0)
        label = Gtk.Label()
        label.set_margin_top(5)
        label.set_margin_bottom(5)
        label.set_justify(Gtk.Justification.CENTER)
        label.set_selectable(True)
        label.set_markup(result[-1][10]+"\n\n"+result[-1][1])
        label.props.ellipsize = Pango.EllipsizeMode.END
        v.pack_start(label,False,False,0)
        v.pack_start(h,False,False,0)
        progb = Gtk.ProgressBar()
        progb.set_show_text(True)
        progb.set_margin_bottom(10)
        progbhb = Gtk.HBox()
        progbhb.pack_start(progb,True,False,0)
        v.pack_start(progbhb,False,False,0)
        h2 = Gtk.HBox()
        v.pack_start(h2,True,True,0)
        v1 = Gtk.VBox()
        v2 = Gtk.VBox()
        v3 = Gtk.VBox()
        h2.pack_start(v2,True,False,0)
        h2.pack_start(v3,True,False,0)
        #ggg = GstWidget(result[-1][4],self)
        thumbnails = result[-1][-1]
        ggg = Gtk.Image()
        if  thumbnails:
            url_ = thumbnails[0]["url"]
        else:
            url_ = result[-1][3]
        if "ytimg" in url_:
            url_ = url_.split("?")[0]
        file__ = Gio.File.new_for_uri(url_)
        file__.read_async(1,None,self.on_load_image_finish,ggg)

        
        if not win:
            v1.pack_start(ggg,False,False,0)
        store = Gtk.ListStore(str,str,str,str,str,int,int,str,str,str,str)

        for i in result:
            store.append(i[:-2])
        


        combo = Gtk.ComboBox.new_with_model(store)
        renderer_text = Gtk.CellRendererText()
        renderer_text.props.ellipsize  = Pango.EllipsizeMode.END
        renderer_text.props.max_width_chars = 20
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 9)
        combo.set_active(len(store)-1)
        combo.show_all()
        
        subtitles = result[-1][-2]
        store2 = Gtk.ListStore(str,str,str)
        
        if not subtitles:
            store2.append(["","",""])
        else:
            for k,v in subtitles.items():
                for i in v:
                    store2.append([k+"-"+i["ext"],i["ext"],i["url"]])
                store2.append([k+"-"+"best","best",""])
            store2.append(["","",""])
                
        combo2 = Gtk.ComboBox.new_with_model(store2)
        renderer_text2 = Gtk.CellRendererText()
        renderer_text2.props.ellipsize  = Pango.EllipsizeMode.END
        renderer_text2.props.max_width_chars = 20
        combo2.pack_start(renderer_text2, True)
        combo2.add_attribute(renderer_text2, "text", 0)
        combo2.set_active(len(store2)-1)
        combo2.show_all()
        
        close_button = Gtk.Button()
        close_button.props.label = _("Remove Task")
        button = Gtk.Button()
        button.props.label = _("Download")
        cancel_button = Gtk.Button()
        cancel_button.props.label = _("Cancel")
        cancel_button.set_sensitive(False)
        v2.pack_start(combo,True,False,0)
        v2.pack_start(combo2,True,False,0)
        v2.pack_start(close_button,True,False,0)
        v3.pack_start(button,True,False,0)
        v3.pack_start(cancel_button,True,False,0)
        
        if not win:
            h.pack_start(v1,True,False,0)

        button.connect("clicked",self.on_download,progb,store,combo,cancel_button,close_button,store2,combo2)
        close_button.connect("clicked",self.on_close,row,result)
        self.show_all()
        progb.hide()
        
    def on_close(self,button,row,result,force=False): 
        if not force:
            self.infobar2.hide__()
            self.infobar2.label.props.label = _("Are You Sure\nYou Want To Remove This Task?")
            self.infobar2.send_button = True
            self.infobar2.b.props.label = _("Remove")
            self.infobar2.row    = row
            self.infobar2.result = result
            self.infobar2.func   = self.on_close
            self.infobar2.show__()
            return
        self.listbox.remove(row)
        row.destroy()
        url = result[0][-3]
        if url in self.all_video_info.keys():
            del self.all_video_info[url]
        self.config__["current_links"].remove(result)
        change_metadata_info(self.config__)

        
    def on_download(self,button,progressbar,store,combo,cancel_button,close_button,store2,combo2):
        subtitle    = store2[combo2.get_active_iter()][0]
        if self.use_password_switch.get_active():
            username = self.name_entry.get_text().strip()
            password=self.password_entry.get_text().strip()
            videopassword=self.video_pass_entry.get_text().strip()
            if not username and not password:
                username = ""
                password = ""
        else:
            username = ""
            password = ""
            videopassword = ""
        self.password_entry.set_text("")
        self.video_pass_entry.set_text("")
            
        t = DownloadFile(self,
                         progressbar=progressbar,
                         button=button,
                         link=store[combo.get_active_iter()][-1],
                         location=GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_VIDEOS),
                         format_=store[combo.get_active_iter()][-4],
                         username=username,
                         password=password,
                         videopassword=videopassword,
                         cancel_button=cancel_button,
                         close_button=close_button,
                         subtitle=subtitle)
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
        
    def on_entry_icon_press(self,entry, icon_pos, event):
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
        self.stack1.child_set_property(self.vbox3, 'needs-attention', True) 
            
           
        
    def on_paste_button_clicked(self,button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD  )
        text = clipboard.wait_for_text()
        if text:
            self.link_entry.set_text(text)
            
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
            GLib.idle_add(self.vbox2.pack_start,self.check_youtube_dl_update_button,False,False,0)
            GLib.idle_add(self.vbox.set_sensitive,True)
            GLib.idle_add(self.check_youtube_dl_update_button.set_sensitive,True)
        else:
            GLib.idle_add(self.statuspage2.set_description,(_("New Version : ")+last_version))
            GLib.idle_add(self.check_for_update_infobar.label.set_label ,"Please Restart Pysavetube")
            GLib.idle_add(self.check_for_update_infobar.show__)
        self.__isinstall = True
        GLib.idle_add(self.installbutton.set_sensitive,True)
        GLib.idle_add(self.show_all)

        
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
            GLib.idle_add(self.installbutton.emit,"clicked")
            
        GLib.idle_add(self.check_for_update_infobar.label.set_label ,msg)
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
            self.window.connect("delete-event",self.on_quit)
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

