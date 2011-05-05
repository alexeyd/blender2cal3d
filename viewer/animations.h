#ifndef ANIMATIONS_H
#define ANIMATIONS_H

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

class AnimationsControl
{
  public:
    AnimationsControl(const core::position2d<s32> & pos);

  protected:
    gui::IGUIWindow *window;
    gui::IGUIListBox *animations_listbox;

    static bool animations_listbox_handler(gui::IGUIElement *self,
                                           gui::IGUIElement *other,
                                           void *data,
                                           gui::EGUI_EVENT_TYPE event);
};

#endif 

