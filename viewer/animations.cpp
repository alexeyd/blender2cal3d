#include "animations.h"
 
AnimationsControl::AnimationsControl(const core::position2d<s32> & pos)
{
  using namespace gui;
  IGUIEnvironment *gui_env = device->getGUIEnvironment();

  core::position2d<s32> window_lo, window_hi;
  window_lo = pos;
  window_hi = pos + core::position2d<s32>(170, 100);
  window = gui_env->addWindow(core::rect<s32>(window_lo, window_hi),
                              false, L"Animations");

  core::position2d<s32> widget_origin;

  widget_origin = window->getClientRect().UpperLeftCorner;

  const core::rect< s32 >
    window_rect(window->getClientRect().UpperLeftCorner.X,
                window->getClientRect().UpperLeftCorner.Y,
                window->getClientRect().getWidth(),
                window->getClientRect().getHeight());


  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 10,
                  window->getClientRect().UpperLeftCorner.Y + 10,
                  window->getClientRect().UpperLeftCorner.X + 150,
                  window->getClientRect().UpperLeftCorner.Y + 70);
    animations_listbox = gui_env->addListBox(widget_rect, window);
    animations_listbox->addItem(L"None");
  }

  GUIEventReceiver *recver = GUIEventReceiver::instance();
  GUICallbackHandler h;

  h.handler = animations_listbox_handler;
  h.caller = animations_listbox;
  h.data = NULL;
  recver->handlers.push_back(h);
}


bool AnimationsControl::animations_listbox_handler(gui::IGUIElement *self,
                                                   gui::IGUIElement *other,
                                                   void *data,
                                                   gui::EGUI_EVENT_TYPE event)
{
  using namespace gui;

  IGUIListBox *animations_listbox = (IGUIListBox*) self;

  if((event == EGET_ELEMENT_FOCUS_LOST) ||
     (event == EGET_ELEMENT_FOCUSED)    ||
     (event == EGET_ELEMENT_HOVERED)    ||
     (event == EGET_ELEMENT_LEFT)         )
  {
    return false;
  }

  if(!model || !node)
  {
    return false;
  }

  const c8 *anim_name;
  wchar_t wname[8192];

  if(event == EGET_COUNT)
  {

    /* get animations' names */
    animations_listbox->clear();

    animations_listbox->addItem(L"None");

    for(int i = 0; i < model->getAnimationCount(); ++i)
    {
      anim_name = model->getAnimationName(i);
      mbstowcs(wname, anim_name, 8192);
      wname[8191] = 0;
      animations_listbox->addItem(wname);
    }
  }
  else
  {
    u32 selected_id = (u32) animations_listbox->getSelected();
    const wchar_t *selected = animations_listbox->getListItem(selected_id);

    for(int i=0; i < node->getAnimationCount(); ++i)
    {
      node->stopAnimation(i);
    }

    if(wcscmp(selected, L"None") == 0)
    {
    }
    else
    {
      for(int i=0; i < node->getAnimationCount(); ++i)
      {
        anim_name = model->getAnimationName(i);
        mbstowcs(wname, anim_name, 8192);
        wname[8191] = 0;
        if(wcscmp(selected, wname) == 0)
        {
          node->playAnimation(anim_name);
          break;
        }
      }
    }
  }

  return false;
}

