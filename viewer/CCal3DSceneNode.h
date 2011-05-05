#ifndef _C_CAL3D_SCENE_NODE_H_
#define _C_CAL3D_SCENE_NODE_H_

#include <irrlicht.h>
#include "irrCal3DConfig.h"

class CalModel;

namespace irr
{
namespace scene
{

class CCal3DModel;

enum Cal3DDrawMode
{
  DM_DEFAULT,
  DM_WIREFRAME,
  DM_SKELETON,
  DM_WIREFRAME_AND_SKELETON
};

class IRRCAL3D_API CCal3DSceneNode : public ISceneNode
{
public:
    //! Returns the model used by this scene node
    CCal3DModel* getModel() const;

    //! Returns the bounding box
    //! Note that the bounding box will not change to reflect the character's animation
    const core::aabbox3d<f32>& getBoundingBox() const;


    //! Set new bounding box for a node
    //! Note that the bounding box will not change to reflect the character's animation
    void setBoundingBox(core::aabbox3d<f32>& bbox);
    
    //! Returns the material.
    //! Certain flags like lighting are always used, where others are taken from the
    //! cal3d model.
    virtual video::SMaterial& getMaterial( u32 i );
    
    //! Returns 1.
    virtual u32 getMaterialCount();
    
    //! See setOverrideMaterial
    bool isOverrideMaterialSet() const;
    
    //! Override material is disabled by default.
    //! If enabled, the cal3d material will be ignored completely.
    void setOverrideMaterial( bool flag );
    
    //! Returns the number of animations. Same as calling getAnimationCount for the model.
    s32 getAnimationCount() const;


    Cal3DDrawMode drawMode();
    void drawMode(Cal3DDrawMode new_draw_mode);

    bool drawBBox();
    void drawBBox(bool new_draw_bbox);


    bool drawNormals();
    void drawNormals(bool new_normals);
    
    //! Plays an animation. delay is the number of seconds it takes to fade over to
    //! the new animation. weight is how great influence the animation has in relation to
    //! other animations. High weight means more influence. If there is only one animation
    //! playing, then the weight can be anything (except 0).
    //! id is the number of the animation to play. 0 is always the first animation.
    //! Note: Calling playAnimation will not stop the previous animation. The animation
    //! you start will keep looping until stopped using stopAnimation.
    bool playAnimation( s32 id, f32 delay=0.0f, f32 weight=1.0f );
    
    //! Overloaded playAnimation that takes the name of the animation instead.
    //! See CCal3DModel::getAnimationId
    bool playAnimation( const c8* animName, f32 delay=0.0f, f32 weight=1.0f );
    
    //! Stops an animation. delay is the number of seconds it takes for the animation
    //! to fade away.
    bool stopAnimation( s32 id, f32 delay=0.0f );
    
    //! Overloaded stopAnimation that takes the name of the animation instead.
    //! See CCal3DModel::getAnimationId
    bool stopAnimation( const c8* animName, f32 delay=0.0f );
 
    //! Plays an animation once. See playAnimation for details about the parameters.
    bool playAnimationOnce( s32 id, f32 weight=1.0f, f32 delayIn=0.0f, f32 delayOut=0.0f );
    
    //! Same as above, but takes an animation name instead of the number.
    bool playAnimationOnce( const c8* animName, f32 weight=1.0f, f32 delayIn=0.0f, f32 delayOut=0.0f );
    
    //! Skips forward in animation.
    void adjustAnimationTime( f32 deltaTime, bool applyTimeScale=false );
    
    //! Skips to a certain point in animation.
    void setAnimationTime( f32 setTime );
    
    //! High time scale increases the speed of animations, where low time scale is slow-motion.
    //! Default is 1.0, which is normal time.
    void setTimeScale( f32 timeScale );
    
    //! Returns the current time scale.
    f32 getTimeScale() const;
    
    //! Returns the number of bones on the cal3d model.
    s32 getBoneCount() const;
    
    //! Returns the transformation matrix for one bone. The matrix is relative to the
    //! scene node (not be bone's parent).
    //! Useful for attaching a weapon to a soldiers hand, for example.
    core::matrix4 getBoneMatrix( s32 boneId ) const;
    
    virtual void OnRegisterSceneNode();
    virtual void render();
    virtual void OnAnimate( u32 timeMs );
    
    // Constructor for the cal3d scene node. Create a cal3d model and then call this.
    CCal3DSceneNode( CCal3DModel* model, ISceneNode* parent, ISceneManager* manager, s32 id=-1,
            const core::vector3df& position = core::vector3df(0,0,0),
            const core::vector3df& rotation = core::vector3df(0,0,0),
            const core::vector3df& scale = core::vector3df(1,1,1) );
    
    //! Destructor
    virtual ~CCal3DSceneNode();
    
private:
    CCal3DModel* Model;
    CalModel* calModel;
    Cal3DDrawMode draw_mode;
    bool draw_bbox;
    bool draw_normals;
    
    video::SMaterial Material;
    core::aabbox3d<f32> BoundingBox;
    
    bool OverrideMaterial;
    
    f32 TimeScale;
    s32 LastUpdateTime;
};

} // namespace scene
} // namespace irr

#endif // _C_CAL3D_SCENE_NODE_H_

