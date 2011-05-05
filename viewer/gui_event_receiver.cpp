#include "gui_event_receiver.h"


GUIEventReceiver::GUIEventReceiver()
{
}

bool GUIEventReceiver::OnEvent(const SEvent &event)
{
  using namespace gui;
  const SEvent::SGUIEvent *gui_event;
  vector<GUICallbackHandler>::iterator h;
  bool result = false;

  if(event.EventType == EET_GUI_EVENT)
  {
    gui_event = &(event.GUIEvent);

    for(h = handlers.begin();
        h != handlers.end();
        h++)
    {
      /* when caller is not set, it's a broadcast event for all
       * subscribers 
       */
      if(h->caller == gui_event->Caller || gui_event->Caller == NULL)
      {
        result = h->handler(h->caller, gui_event->Element, 
                            h->data, gui_event->EventType);

        /* not a broadcast */
        if(gui_event->Caller)
        {
          break;
        }
      }
    }
  }

  return result;
}

GUIEventReceiver* GUIEventReceiver::the_receiver = NULL;

GUIEventReceiver* GUIEventReceiver::instance()
{
  if(!the_receiver)
  {
    the_receiver = new GUIEventReceiver();
  }

  return the_receiver;
}

