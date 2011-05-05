#ifndef GUI_EVENT_RECEIVER_H
#define GUI_EVENT_RECEIVER_H

#include <irrlicht.h>
#include <iostream>
#include <stdio.h>
#include <wchar.h>
#include <vector>

using namespace irr;
using namespace std;

class GUIEventReceiver;

struct GUICallbackHandler
{
  gui::IGUIElement *caller;
  void *data;
  bool (*handler)(gui::IGUIElement *self,
                  gui::IGUIElement *other,
                  void *data,
                  gui::EGUI_EVENT_TYPE event);
};

class GUIEventReceiver : public IEventReceiver
{
  public:
    virtual bool OnEvent(const SEvent &event);

    static GUIEventReceiver* instance();

    vector<GUICallbackHandler> handlers;

  protected:
    GUIEventReceiver();

    static GUIEventReceiver *the_receiver;
};

#endif

