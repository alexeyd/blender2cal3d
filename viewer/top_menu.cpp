#include "top_menu.h"


TopMenuControl::TopMenuControl()
{
  using namespace gui;

  IGUIEnvironment *gui_env = device->getGUIEnvironment();

  top_menu = gui_env->addMenu();
  u32 file_id = top_menu->addItem(L"File", -1, true, true);
  
  IGUIContextMenu *file_submenu = top_menu->getSubMenu(file_id);
  file_submenu->addItem(L"Open...");
  file_submenu->addItem(L"Quit");


  GUIEventReceiver *recver = GUIEventReceiver::instance();
  GUICallbackHandler h;

  h.handler = file_submenu_handler;
  h.caller = file_submenu;
  h.data = NULL;
  recver->handlers.push_back(h);
}


bool TopMenuControl::file_submenu_handler(gui::IGUIElement *self, 
                                          gui::IGUIElement *caller,
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

  IGUIEnvironment *gui_env = device->getGUIEnvironment();

  IGUIContextMenu *menu = (IGUIContextMenu *) self;
  u32 item_id = (u32) menu->getSelectedItem();
  if(wcscmp(menu->getItemText(item_id), L"Open...") == 0)
  {
    IGUIFileOpenDialog *fopen_dialog = 
      gui_env->addFileOpenDialog(L"Open cal3d file");

    GUIEventReceiver *recver = GUIEventReceiver::instance();
    GUICallbackHandler h;
 
    h.handler = file_open_handler;
    h.caller = fopen_dialog;
    h.data = NULL;
    recver->handlers.push_back(h);
  }
  else if(wcscmp(menu->getItemText(item_id), L"Quit") == 0)
  {
    quit_clicked = true;
  }

  return false;
}


bool TopMenuControl::file_open_handler(gui::IGUIElement *self, 
                                       gui::IGUIElement *caller,
                                       void *data,
                                       gui::EGUI_EVENT_TYPE event)
{
  using namespace gui;

  if(event == EGET_FILE_SELECTED)
  {
    IGUIFileOpenDialog *fopen_dialog = 
      (IGUIFileOpenDialog*) self;


    wcstombs(cfg_filename, fopen_dialog->getFileName(), 8192);
    cfg_filename[8191] = 0;

    if(model)
    {
      delete model;
    }

    model = new scene::CCal3DModel();

    if(model->loadFromFile(device->getVideoDriver(), cfg_filename))
    {
      if(node)
      {
        delete node;
      }

      scene::ISceneManager* manager = device->getSceneManager();
      node = new scene::CCal3DSceneNode(model, 
                                        manager->getRootSceneNode(), 
                                        manager);

      node->getMaterial(0).setFlag(video::EMF_LIGHTING, false);

      /* generate onload event for other widgets */
      SEvent event;
      event.EventType = EET_GUI_EVENT;
      event.GUIEvent.Caller = NULL;
      event.GUIEvent.Element = NULL;
      event.GUIEvent.EventType = EGET_COUNT; /* uhm... let it be onload (= */
      GUIEventReceiver::instance()->OnEvent(event);
    }
  }

  return false;
}

