#ifndef _C_CAL3D_MODEL_H_
#define _C_CAL3D_MODEL_H_

#include <irrlicht.h>
#include "irrCal3DConfig.h"

class CalCoreModel;

namespace irr
{
namespace scene
{

class IRRCAL3D_API CCal3DModel : public IReferenceCounted
{
public:
    //! Used by CCal3DSceneNode. You don't need to call this yourself
    //! unless you want to manipulate the model using the cal3d API directly.
    CalCoreModel*   getCalCoreModel() const;
    
    //! Returns the bounding box. The bounding box will contain the model
    //! as it appears in the reference frame (also known as frame #0).
    //! Models usually stand in a T-shirt position with the arms out the sides.
    //! Because of this, the bounding box tends to be a big larger than expected.
    const core::aabbox3d<f32>& getBoundingBox() const;
    
    //! Returns the number of animations supported by the model
    s32 getAnimationCount() const;
    
    //! Changes the name of an animation.
    void setAnimationName( s32 animationId, const c8* animationName );

    //! Returns the name of the animation with this ID.
    const c8* getAnimationName(s32 id) const;
    
    //! Returns the ID of the animation with this name.
    //! An animation's name can be set it the .cfg file for the cal3d model.
    //! By writing animationname=walk, the following animation will be given that name.
    s32 getAnimationId( const c8* animationName ) const;

    float getAnimationDuration(const c8 *animationName) const;
    float getAnimationDuration(s32 id) const;
    
    //! Loads the model from a file. Until you call this, the model will be empty.
    //! The filename should point to the .cfg file. All the other files will be loaded
    //! from there, and textures will be created using the video driver.
    bool loadFromFile( video::IVideoDriver* driver, const c8* filename );
    
    //! Creates an empty cal3d model. Call loadFromFile before using it.
    CCal3DModel();
    virtual ~CCal3DModel();
    
private:
    CalCoreModel* Model;
   
    bool predefined_bbox;
    core::aabbox3d<f32> BoundingBox;
    
    s32 AnimationCount;
};

} // namespace scene
} // namespace irr

#endif // _C_CAL3D_MODEL_H_

