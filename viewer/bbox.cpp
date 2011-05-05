#include "bbox.h"
 
BBoxControl::BBoxControl(const core::position2d<s32> & pos)
{
  using namespace gui;
  IGUIEnvironment *gui_env = device->getGUIEnvironment();

  core::position2d<s32> window_lo, window_hi;
  window_lo = pos;
  window_hi = pos + core::position2d<s32>(160, 130);
  window = gui_env->addWindow(core::rect<s32>(window_lo, window_hi),
                              false, L"Bounding Box");

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
                  window->getClientRect().UpperLeftCorner.X + 30,
                  window->getClientRect().UpperLeftCorner.Y + 25);
    gui_env->addStaticText(L"LX:", widget_rect, false, false, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 30,
                  window->getClientRect().UpperLeftCorner.Y + 10,
                  window->getClientRect().UpperLeftCorner.X + 70,
                  window->getClientRect().UpperLeftCorner.Y + 25);
    lx_editbox = gui_env->addEditBox(L"0.0", widget_rect, true, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 10,
                  window->getClientRect().UpperLeftCorner.Y + 35,
                  window->getClientRect().UpperLeftCorner.X + 30,
                  window->getClientRect().UpperLeftCorner.Y + 50);
    gui_env->addStaticText(L"LY:", widget_rect, false, false, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 30,
                  window->getClientRect().UpperLeftCorner.Y + 35,
                  window->getClientRect().UpperLeftCorner.X + 70,
                  window->getClientRect().UpperLeftCorner.Y + 50);
    ly_editbox = gui_env->addEditBox(L"0.0", widget_rect, true, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 10,
                  window->getClientRect().UpperLeftCorner.Y + 60,
                  window->getClientRect().UpperLeftCorner.X + 30,
                  window->getClientRect().UpperLeftCorner.Y + 75);
    gui_env->addStaticText(L"LZ:", widget_rect, false, false, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 30,
                  window->getClientRect().UpperLeftCorner.Y + 60,
                  window->getClientRect().UpperLeftCorner.X + 70,
                  window->getClientRect().UpperLeftCorner.Y + 75);
    lz_editbox = gui_env->addEditBox(L"0.0", widget_rect, true, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 80,
                  window->getClientRect().UpperLeftCorner.Y + 10,
                  window->getClientRect().UpperLeftCorner.X + 100,
                  window->getClientRect().UpperLeftCorner.Y + 25);
    gui_env->addStaticText(L"HX:", widget_rect, false, false, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 100,
                  window->getClientRect().UpperLeftCorner.Y + 10,
                  window->getClientRect().UpperLeftCorner.X + 140,
                  window->getClientRect().UpperLeftCorner.Y + 25);
    hx_editbox = gui_env->addEditBox(L"0.0", widget_rect, true, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 80,
                  window->getClientRect().UpperLeftCorner.Y + 35,
                  window->getClientRect().UpperLeftCorner.X + 100,
                  window->getClientRect().UpperLeftCorner.Y + 50);
    gui_env->addStaticText(L"HY:", widget_rect, false, false, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 100,
                  window->getClientRect().UpperLeftCorner.Y + 35,
                  window->getClientRect().UpperLeftCorner.X + 140,
                  window->getClientRect().UpperLeftCorner.Y + 50);
    hy_editbox = gui_env->addEditBox(L"0.0", widget_rect, true, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 80,
                  window->getClientRect().UpperLeftCorner.Y + 60,
                  window->getClientRect().UpperLeftCorner.X + 100,
                  window->getClientRect().UpperLeftCorner.Y + 75);
    gui_env->addStaticText(L"HZ:", widget_rect, false, false, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 100,
                  window->getClientRect().UpperLeftCorner.Y + 60,
                  window->getClientRect().UpperLeftCorner.X + 140,
                  window->getClientRect().UpperLeftCorner.Y + 75);
    hz_editbox = gui_env->addEditBox(L"0.0", widget_rect, true, window);
  }

  {
    const core::rect< s32 >
      widget_rect(window->getClientRect().UpperLeftCorner.X + 10,
                  window->getClientRect().UpperLeftCorner.Y + 80,
                  window->getClientRect().UpperLeftCorner.X + 140,
                  window->getClientRect().UpperLeftCorner.Y + 100);
    bbox_button = gui_env->addButton(widget_rect, window, -1, L"Apply");
  }

  GUIEventReceiver *recver = GUIEventReceiver::instance();
  GUICallbackHandler h;

  h.handler = bbox_button_handler;
  h.caller = bbox_button;
  h.data = this;
  recver->handlers.push_back(h);
}


bool BBoxControl::bbox_button_handler(gui::IGUIElement *self,
                                      gui::IGUIElement *other,
                                      void *data,
                                      gui::EGUI_EVENT_TYPE event)
{
  using namespace gui;

  BBoxControl *bbc = (BBoxControl*) data;

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


  char buffer[128];
  wchar_t wbuffer[128];
  core::aabbox3d<f32> bbox;

  if(event == EGET_COUNT)
  {
    bbox = node->getBoundingBox();

    sprintf(buffer, "%f",bbox.MinEdge.X);
    mbstowcs(wbuffer, buffer, 128);
    wbuffer[127] = 0;
    bbc->lx_editbox->setText(wbuffer);

    sprintf(buffer, "%f",bbox.MinEdge.Y);
    mbstowcs(wbuffer, buffer, 128);
    wbuffer[127] = 0;
    bbc->ly_editbox->setText(wbuffer);

    sprintf(buffer, "%f",bbox.MinEdge.Z);
    mbstowcs(wbuffer, buffer, 128);
    wbuffer[127] = 0;
    bbc->lz_editbox->setText(wbuffer);


    sprintf(buffer, "%f",bbox.MaxEdge.X);
    mbstowcs(wbuffer, buffer, 128);
    wbuffer[127] = 0;
    bbc->hx_editbox->setText(wbuffer);

    sprintf(buffer, "%f",bbox.MaxEdge.Y);
    mbstowcs(wbuffer, buffer, 128);
    wbuffer[127] = 0;
    bbc->hy_editbox->setText(wbuffer);

    sprintf(buffer, "%f",bbox.MaxEdge.Z);
    mbstowcs(wbuffer, buffer, 128);
    wbuffer[127] = 0;
    bbc->hz_editbox->setText(wbuffer);
  }
  else
  {
    wcstombs(buffer, bbc->lx_editbox->getText(), 128);
    buffer[127] = 0;
    bbox.MinEdge.X = atoi(buffer);

    wcstombs(buffer, bbc->ly_editbox->getText(), 128);
    buffer[127] = 0;
    bbox.MinEdge.Y = atoi(buffer);

    wcstombs(buffer, bbc->lz_editbox->getText(), 128);
    buffer[127] = 0;
    bbox.MinEdge.Z = atoi(buffer);

    wcstombs(buffer, bbc->hx_editbox->getText(), 128);
    buffer[127] = 0;
    bbox.MaxEdge.X = atoi(buffer);

    wcstombs(buffer, bbc->hy_editbox->getText(), 128);
    buffer[127] = 0;
    bbox.MaxEdge.Y = atoi(buffer);

    wcstombs(buffer, bbc->hz_editbox->getText(), 128);
    buffer[127] = 0;
    bbox.MaxEdge.Z = atoi(buffer);


    FILE *cfg_file = fopen(cfg_filename, "r");
    bool found_bbox_string = false;
    int i, line_count;
    static char cfg_file_dump[100][200];

    if(cfg_file)
    {
      for(line_count = 0; 
          fgets(cfg_file_dump[line_count], 199, cfg_file); 
          ++line_count);
      
      fclose(cfg_file);
      cfg_file = fopen(cfg_filename, "w");

      if(cfg_file)
      {
        for(i = 0; i < line_count; ++i)
        {
          if(strstr(cfg_file_dump[i], "bbox"))
          {
            found_bbox_string = true;

            sprintf(cfg_file_dump[i], "bbox = %2.3f %2.3f %2.3f "
                                              "%2.3f %2.3f %2.3f\n",
                    bbox.MinEdge.X, bbox.MinEdge.Y, bbox.MinEdge.Z,
                    bbox.MaxEdge.X, bbox.MaxEdge.Y, bbox.MaxEdge.Z);

          }

          fwrite(cfg_file_dump[i], 1, strlen(cfg_file_dump[i]), cfg_file);
        }

        if(!found_bbox_string)
        {
          fprintf(cfg_file, "bbox = %2.3f %2.3f %2.3f "
                            "%2.3f %2.3f %2.3f\n",
                  bbox.MinEdge.X, bbox.MinEdge.Y, bbox.MinEdge.Z,
                  bbox.MaxEdge.X, bbox.MaxEdge.Y, bbox.MaxEdge.Z);
        }

        fclose(cfg_file);
      }
    }

    node->setBoundingBox(bbox);
  }

  return false;
}

