#ifndef DRAW_MODE_H
#define DRAW_MODE_H

#include <irrlicht.h>
#include <iostream>
#include <stdio.h>
#include <wchar.h>

#include <irrCal3d.h>
#include <cal3d/cal3d.h>

#include "gui_event_receiver.h"

using namespace irr;
using namespace std;

// For the gui id's
enum EGUI_IDS
{
  GUI_ID_OPEN_TEXTURE = 1,
  GUI_ID_QUIT,
  GUI_ID_MAX
};

extern scene::CCal3DSceneNode *node;
extern scene::CCal3DModel *model;
extern IrrlichtDevice* device;

class DrawModeControl
{
  public:
    DrawModeControl(const core::position2d<s32> & pos);

  protected:
    gui::IGUIWindow *window;
    gui::IGUICheckBox *bb_checkbox;
    gui::IGUICheckBox *norm_checkbox;
    gui::IGUIComboBox *draw_mode_combobox;

    static bool bb_checkbox_handler(gui::IGUIElement *self,
                                    gui::IGUIElement *other,
                                    void *data,
                                    gui::EGUI_EVENT_TYPE event);

    static bool norm_checkbox_handler(gui::IGUIElement *self,
                                      gui::IGUIElement *other,
                                      void *data,
                                      gui::EGUI_EVENT_TYPE event);

    static bool draw_mode_combobox_handler(gui::IGUIElement *self,
                                           gui::IGUIElement *other,
                                           void *data,
                                           gui::EGUI_EVENT_TYPE event);
};

#endif 

