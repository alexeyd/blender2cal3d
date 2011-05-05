#ifndef LINE_SEGMENT_SCENE_NODE_H
#define LINE_SEGMENT_SCENE_NODE_H

#include <irrlicht.h>

using namespace irr;


class LineSegmentSceneNode : public scene::ISceneNode
{
  protected:
	  core::aabbox3d<f32> aabb;
    u16 indices[2];
	  video::S3DVertex vertices[2];
	  video::SMaterial material;

    void recalcAABB();

  public:

	  LineSegmentSceneNode(scene::ISceneNode* parent, 
                         scene::ISceneManager* mgr, 
                         s32 id,
                         core::vector3df start,
                         core::vector3df end);

    virtual void OnRegisterSceneNode();
    virtual void render();

    virtual const core::aabbox3d<f32>& getBoundingBox() const;
    virtual u32 getMaterialCount() const;
    virtual video::SMaterial& getMaterial(u32 i);

    void setStart(core::vector3df start);
    void setEnd(core::vector3df end);

    const core::vector3df& getStart() const;
    const core::vector3df& getEnd() const;

    void setColor(const video::SColor &color);
};

#endif

