#include "line_segment_scene_node.h"

void LineSegmentSceneNode::recalcAABB()
{
  aabb.reset(core::vector3df(0.0, 0.0, 0.0));
  for(int i = 0; i < 2; ++i)
  {
    aabb.addInternalPoint(vertices[i].Pos);
    indices[i] = i;
  }
}

LineSegmentSceneNode::LineSegmentSceneNode(scene::ISceneNode* parent, 
                                           scene::ISceneManager* mgr, 
                                           s32 id,
                                           core::vector3df start,
                                           core::vector3df end)
  : scene::ISceneNode(parent, mgr, id)
{
  core::vector3df normal(0.0, 1.0, 0.0);
  core::vector2d<f32> tcoords(0.0, 0.0);

  material.setFlag(video::EMF_LIGHTING, false);

  vertices[0] = video::S3DVertex(start, 
                                 normal,
                                 video::SColor(0xffffffff),
                                 tcoords);


  vertices[1] = video::S3DVertex(end, 
                                 normal,
                                 video::SColor(0xffffffff),
                                 tcoords);
  recalcAABB();
}

void LineSegmentSceneNode::OnRegisterSceneNode()
{
  if (IsVisible)
  {
	  SceneManager->registerNodeForRendering(this);
  }

  ISceneNode::OnRegisterSceneNode();
}

void LineSegmentSceneNode::render()
{
  video::IVideoDriver *driver = SceneManager->getVideoDriver();
  driver->setMaterial(material);
  driver->setTransform(video::ETS_WORLD, AbsoluteTransformation);
  driver->drawVertexPrimitiveList(&(vertices[0]), 2, 
                                  &(indices[0]), 1,
                                  video::EVT_STANDARD,
                                  scene::EPT_LINES, 
                                  video::EIT_16BIT);
}

const core::aabbox3d<f32>& LineSegmentSceneNode::getBoundingBox() const
{
  return aabb;
}

u32 LineSegmentSceneNode::getMaterialCount() const
{
  return 1;
}

video::SMaterial& LineSegmentSceneNode::getMaterial(u32 i)
{
  return material;
}

void LineSegmentSceneNode::setStart(core::vector3df start)
{
  vertices[0].Pos = start;
  recalcAABB();
}

void LineSegmentSceneNode::setEnd(core::vector3df end)
{
  vertices[1].Pos = end;
  recalcAABB();
}

const core::vector3df& LineSegmentSceneNode::getStart() const
{
  return vertices[0].Pos;
}

const core::vector3df& LineSegmentSceneNode::getEnd() const
{
  return vertices[1].Pos;
}

void LineSegmentSceneNode::setColor(const video::SColor &color)
{
  vertices[0].Color = color;
  vertices[1].Color = color;
}




