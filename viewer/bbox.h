#ifndef BBOX_H
#define BBOX_H

#include <irrlicht.h>
#include <iostream>
#include <stdio.h>
#include <wchar.h>

#include <irrCal3d.h>
#include <cal3d/cal3d.h>

#include "gui_event_receiver.h"

using namespace irr;
using namespace std;

extern scene::CCal3DSceneNode *node;
extern scene::CCal3DModel *model;
extern IrrlichtDevice* device;
extern char cfg_filename[8192];

class BBoxControl
{
  public:
    BBoxControl(const core::position2d<s32> & pos);

  protected:
    gui::IGUIWindow *window;

    gui::IGUIEditBox *lx_editbox;
    gui::IGUIEditBox *ly_editbox;
    gui::IGUIEditBox *lz_editbox;

    gui::IGUIEditBox *hx_editbox;
    gui::IGUIEditBox *hy_editbox;
    gui::IGUIEditBox *hz_editbox;

    gui::IGUIButton *bbox_button;

    static bool bbox_button_handler(gui::IGUIElement *self,
                                    gui::IGUIElement *other,
                                    void *data,
                                    gui::EGUI_EVENT_TYPE event);
};

#endif 

