#include <irrlicht.h>
#include <iostream>
#include <stdio.h>
#include <wchar.h>

#include <irrCal3d.h>
#include <cal3d/cal3d.h>

#include "gui_event_receiver.h"
#include "draw_mode.h"
#include "top_menu.h"
#include "animations.h"
#include "bbox.h"

#include "line_segment_scene_node.h"

using namespace irr;

class CEventReceiver : public IEventReceiver
{
  public:
    bool Keys[ KEY_KEY_CODES_COUNT ];
    bool TappedKeys[ KEY_KEY_CODES_COUNT ];
    
    virtual bool OnEvent( const SEvent &event )
    {
      if ( event.EventType == EET_KEY_INPUT_EVENT )
      {
        Keys[ event.KeyInput.Key ] = event.KeyInput.PressedDown;
        TappedKeys[ event.KeyInput.Key ] = event.KeyInput.PressedDown;
      }
      return false;
    }
    
    void update()
    {
      for ( s32 i=0; i<KEY_KEY_CODES_COUNT; i++ )
      {
        TappedKeys[i] = false;
      }
    }
    
    CEventReceiver()
    {
      for ( s32 i=0; i<KEY_KEY_CODES_COUNT; i++ )
      {
        Keys[i] = false;
        TappedKeys[i] = false;
      }
    }
};


scene::CCal3DSceneNode *node = NULL;
scene::CCal3DModel *model = NULL;
IrrlichtDevice *device = NULL;
bool quit_clicked = false;

char cfg_filename[8192];

int main()
{
  device = createDevice( video::EDT_OPENGL );
  device->setWindowCaption(L"Cal3D Model Viewer");
  
  scene::ISceneManager* manager = device->getSceneManager();
  video::IVideoDriver* driver = device->getVideoDriver();
  gui::IGUIEnvironment* gui_env = device->getGUIEnvironment();


  gui::IGUISkin* skin = gui_env->getSkin();
  gui::IGUIFont* font = 
    gui_env->getFont("fonthaettenschweiler.bmp");

  if (font)
  {
    skin->setFont(font);
  }

  /*skin->setFont(env->getBuiltInFont(), EGDF_TOOLTIP);*/

  CEventReceiver eventReceiver;
  device->setEventReceiver( &eventReceiver );
  
  
  manager->addCameraSceneNodeMaya();
  manager->addLightSceneNode(NULL, core::vector3df(-50.0, 50.0, -50.0));

  GUIEventReceiver *gui_event_recver = GUIEventReceiver::instance();
  gui_env->setUserEventReceiver(gui_event_recver);

  DrawModeControl *draw_mode_control = 
    new DrawModeControl(core::position2d<s32>(100, 100));

  TopMenuControl *top_menu_control = new TopMenuControl();

  AnimationsControl *animations_control = 
    new AnimationsControl(core::position2d<s32>(100, 300));

  BBoxControl *bbox_control = 
    new BBoxControl(core::position2d<s32>(100, 500));

  LineSegmentSceneNode *x_axis = 
    new LineSegmentSceneNode(manager->getRootSceneNode(),
                             manager, -1,
                             core::vector3df(0.0,0.0,0.0),
                             core::vector3df(100.0,0.0,0.0));
  LineSegmentSceneNode *y_axis = 
    new LineSegmentSceneNode(manager->getRootSceneNode(),
                             manager, -1,
                             core::vector3df(0.0,0.0,0.0),
                             core::vector3df(0.0,100.0,0.0));
  LineSegmentSceneNode *z_axis = 
    new LineSegmentSceneNode(manager->getRootSceneNode(),
                             manager, -1,
                             core::vector3df(0.0,0.0,0.0),
                             core::vector3df(0.0,0.0,100.0));

  x_axis->setColor(video::SColor(0xffff0000));
  y_axis->setColor(video::SColor(0xff00ff00));
  z_axis->setColor(video::SColor(0xff0000ff));
  
  while (device->run()  && !quit_clicked)
  {
    driver->beginScene( true, true, video::SColor(0,255,255,255) );
    
    manager->drawAll();
    gui_env->drawAll();
    driver->endScene();
    
    if ( eventReceiver.TappedKeys[ KEY_KEY_W ] )
    {
    }
    
    eventReceiver.update();
  }
  
  device->drop();

  return 0;
}

