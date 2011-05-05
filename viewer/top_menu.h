#ifndef TOP_MENU_H
#define TOP_MENU_H

#include <irrlicht.h>
#include <iostream>
#include <stdio.h>
#include <wchar.h>

#include <irrCal3d.h>
#include <cal3d/cal3d.h>

#include "gui_event_receiver.h"

using namespace irr;
using namespace std;

#define DIR_LIMIT "/"


extern scene::CCal3DSceneNode *node;
extern scene::CCal3DModel *model;
extern IrrlichtDevice* device;
extern bool quit_clicked;
extern char cfg_filename[8192];

class TopMenuControl
{
  public:
    TopMenuControl();


  protected:
    gui::IGUIContextMenu *top_menu;

    static bool file_submenu_handler(gui::IGUIElement *self, 
                                     gui::IGUIElement *caller,
                                     void *data,
                                     gui::EGUI_EVENT_TYPE event);

    static bool file_open_handler(gui::IGUIElement *self, 
                                  gui::IGUIElement *caller,
                                  void *data,
                                  gui::EGUI_EVENT_TYPE event);
};

#endif 

