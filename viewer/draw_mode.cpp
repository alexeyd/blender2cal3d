#include "draw_mode.h"

DrawModeControl::DrawModeControl(const core::position2d<s32> & pos)
{
  using namespace gui;
  IGUIEnvironment *gui_env = device->getGUIEnvironment();

  core::position2d<s32> window_lo, window_hi;
  window_lo = pos;
  window_hi = pos + core::position2d<s32>(120, 95);
  window = gui_env->addWindow(core::rect<s32>(window_lo, window_hi),
                              false, L"Draw Mode");

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
                  window->getClientRect().UpperLeftCorner.X + 105,
                   window->getClientRect().UpperLeftCorner.Y + 20);
    bb_checkbox = gui_env->addCheckBox(false,
                                       widget_rect,
                                       window, -1,
                                       L"draw bbox");
  }


  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 10,
                  window->getClientRect().UpperLeftCorner.Y + 30,
                  window->getClientRect().UpperLeftCorner.X + 105,
                   window->getClientRect().UpperLeftCorner.Y + 40);
    norm_checkbox = gui_env->addCheckBox(false,
                                         widget_rect,
                                         window, -1,
                                         L"draw normals");
  }


  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 10,
                     window->getClientRect().UpperLeftCorner.Y + 50,
                     window->getClientRect().UpperLeftCorner.X + 100,
                     window->getClientRect().UpperLeftCorner.Y + 65);
    draw_mode_combobox = gui_env->addComboBox(widget_rect,
                                              window, -1);
    draw_mode_combobox->addItem(L"default");
    draw_mode_combobox->addItem(L"wireframe");
    draw_mode_combobox->addItem(L"skeleton");
    draw_mode_combobox->addItem(L"skeleton+wireframe");
  }

  GUIEventReceiver *recver = GUIEventReceiver::instance();
  GUICallbackHandler h;

  h.handler = bb_checkbox_handler;
  h.caller = bb_checkbox;
  h.data = NULL;
  recver->handlers.push_back(h);

  h.handler = norm_checkbox_handler;
  h.caller = norm_checkbox;
  h.data = NULL;
  recver->handlers.push_back(h);

  h.handler = draw_mode_combobox_handler;
  h.caller = draw_mode_combobox;
  h.data = NULL;
  recver->handlers.push_back(h);
}


bool DrawModeControl::bb_checkbox_handler(gui::IGUIElement *self,
                                          gui::IGUIElement *other,
                                          void *data,
                                          gui::EGUI_EVENT_TYPE event)
{
  using namespace gui;

  if((event == EGET_ELEMENT_FOCUS_LOST) ||
     (event == EGET_ELEMENT_FOCUSED)    ||
     (event == EGET_ELEMENT_HOVERED)    ||
     (event == EGET_ELEMENT_LEFT)       ||
     (event == EGET_COUNT)                )
  {
    return false;
  }

  if(node)
  {
    IGUICheckBox *bb_checkbox = (IGUICheckBox*) self;
    node->drawBBox(bb_checkbox->isChecked());
  }

  return false;
}


bool DrawModeControl::norm_checkbox_handler(gui::IGUIElement *self,
                                          gui::IGUIElement *other,
                                          void *data,
                                          gui::EGUI_EVENT_TYPE event)
{
  using namespace gui;

  if((event == EGET_ELEMENT_FOCUS_LOST) ||
     (event == EGET_ELEMENT_FOCUSED)    ||
     (event == EGET_ELEMENT_HOVERED)    ||
     (event == EGET_ELEMENT_LEFT)       ||
     (event == EGET_COUNT)                )
  {
    return false;
  }

  if(node)
  {
    IGUICheckBox *norm_checkbox = (IGUICheckBox*) self;
    node->drawNormals(norm_checkbox->isChecked());
  }

  return false;
}


bool DrawModeControl::draw_mode_combobox_handler(gui::IGUIElement *self,
                                                 gui::IGUIElement *other,
                                                 void *data,
                                                 gui::EGUI_EVENT_TYPE event)
{
  using namespace gui;
  using namespace scene;

  if((event == EGET_ELEMENT_FOCUS_LOST) ||
     (event == EGET_ELEMENT_FOCUSED)    ||
     (event == EGET_ELEMENT_HOVERED)    ||
     (event == EGET_ELEMENT_LEFT)       ||
     (event == EGET_COUNT)                )
  {
    return false;
  }

  if(node)
  {
    IGUIComboBox *draw_mode_combobox = (IGUIComboBox*) self;
    u32 selected_id = draw_mode_combobox->getSelected();
    const wchar_t *selected = draw_mode_combobox->getItem(selected_id);

    if(wcscmp(selected, L"default") == 0)
    {
      node->drawMode(DM_DEFAULT);
    }
    else if(wcscmp(selected, L"wireframe") == 0)
    {
      node->drawMode(DM_WIREFRAME);
    }
    else if(wcscmp(selected, L"skeleton") == 0)
    {
      node->drawMode(DM_SKELETON);
    }
    else if(wcscmp(selected, L"skeleton+wireframe") == 0)
    {
      node->drawMode(DM_WIREFRAME_AND_SKELETON);
    }
  }

  return false;
}

