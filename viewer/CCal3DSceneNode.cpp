#include "CCal3DSceneNode.h"
#include "CCal3DModel.h"

// Note: Make sure you #define CAL_16BIT_INDICES in "global.h" or in project settings
#include <cal3d/cal3d.h>

#define EXTENT_K (0.3)
#define SKELETON_K (0.01)
#define NORMAL_K (0.1)

namespace irr
{
namespace scene
{

CCal3DModel* CCal3DSceneNode::getModel() const
{
    return Model;
}

const core::aabbox3d<f32>& CCal3DSceneNode::getBoundingBox() const
{
    return BoundingBox;
}


void CCal3DSceneNode::setBoundingBox(core::aabbox3d<f32>& bbox)
{
  BoundingBox = bbox;
}

video::SMaterial& CCal3DSceneNode::getMaterial( u32 i )
{
    return Material;
}

u32 CCal3DSceneNode::getMaterialCount()
{
    return 1;
}

bool CCal3DSceneNode::isOverrideMaterialSet() const
{
    return OverrideMaterial;
}

void CCal3DSceneNode::setOverrideMaterial( bool flag )
{
    OverrideMaterial = flag;
}

s32 CCal3DSceneNode::getAnimationCount() const
{
    if ( Model != 0 )
    {
        return Model->getAnimationCount();
    }
    else
    {
        return 0;
    }
}

bool CCal3DSceneNode::playAnimation( s32 id, f32 delay, f32 weight )
{
    if ( calModel == 0 ) return false;
    
    return calModel->getMixer()->blendCycle( id, weight, delay );
}

bool CCal3DSceneNode::playAnimation( const c8* animName, f32 delay, f32 weight )
{
    if ( calModel == 0 ) return false;
    
    s32 id = Model->getAnimationId( animName );
    
    return calModel->getMixer()->blendCycle( id, weight, delay );
}

bool CCal3DSceneNode::stopAnimation( s32 id, f32 delay )
{
    if ( calModel == 0 ) return false;
    
    return calModel->getMixer()->clearCycle( id, delay );
}

bool CCal3DSceneNode::stopAnimation( const c8* animName, f32 delay )
{
    if ( calModel == 0 ) return false;
    
    s32 id = Model->getAnimationId( animName );
    
    return calModel->getMixer()->clearCycle( id, delay );
}

bool CCal3DSceneNode::playAnimationOnce( s32 id, f32 delayIn, f32 delayOut, f32 weight )
{
    if ( calModel == 0 ) return false;
    
    return calModel->getMixer()->executeAction( id, delayIn, delayOut, weight );
}

bool CCal3DSceneNode::playAnimationOnce( const c8* animName, f32 delayIn, f32 delayOut, f32 weight )
{
    if ( calModel == 0 ) return false;
    
    s32 id = Model->getAnimationId( animName );
    
    return calModel->getMixer()->executeAction( id, delayIn, delayOut, weight );
}

void CCal3DSceneNode::adjustAnimationTime( f32 deltaTime, bool applyTimeScale )
{
    if ( calModel == 0 ) return;
    
    if ( applyTimeScale )
    {
        calModel->getMixer()->updateAnimation( deltaTime * TimeScale );
    }
    else
    {
        calModel->getMixer()->updateAnimation( deltaTime );
    }
}

void CCal3DSceneNode::setAnimationTime( f32 setTime )
{
    if ( calModel == 0 ) return;
    
    calModel->getMixer()->setAnimationTime( setTime );
}

void CCal3DSceneNode::setTimeScale( f32 timeScale )
{
    TimeScale = timeScale;
}

f32 CCal3DSceneNode::getTimeScale() const
{
    return TimeScale;
}

s32 CCal3DSceneNode::getBoneCount() const
{
    if ( calModel == 0 ) return 0;
    
    return calModel->getSkeleton()->getVectorBone().size();
}

core::matrix4 CCal3DSceneNode::getBoneMatrix( s32 boneId ) const
{
    if ( calModel == 0 ) return core::matrix4();
    
    CalSkeleton* skeleton = calModel->getSkeleton();
    CalBone* bone = skeleton->getBone(boneId);
    
    CalQuaternion rot = bone->getRotationAbsolute();
    CalVector pos = bone->getTranslationAbsolute();
    
    // Note: Swap Y and Z to convert to Irrlicht coordinates
    core::quaternion quat = core::quaternion( rot.x, rot.y, rot.z, rot.w );
    core::vector3df v = core::vector3df( pos.x, pos.y, pos.z );
    
    core::matrix4 mat = quat.getMatrix();
    mat.setTranslation(v);
    
    return mat;
}


Cal3DDrawMode CCal3DSceneNode::drawMode()
{
  return draw_mode;
}


void CCal3DSceneNode::drawMode(Cal3DDrawMode new_draw_mode)
{
  draw_mode = new_draw_mode;
}


bool CCal3DSceneNode::drawBBox()
{
  return draw_bbox;
}

void CCal3DSceneNode::drawBBox(bool new_draw_bbox)
{
  draw_bbox = new_draw_bbox;
}

bool CCal3DSceneNode::drawNormals()
{
  return draw_normals;
}

void CCal3DSceneNode::drawNormals(bool new_draw_normals)
{
  draw_normals = new_draw_normals;
}

void CCal3DSceneNode::OnRegisterSceneNode()
{
    if ( IsVisible && calModel != 0 )
    {
        SceneManager->registerNodeForRendering( this );
    }
    ISceneNode::OnRegisterSceneNode();
}


void CCal3DSceneNode::render()
{
    //----------------------------------------------------------//
    if ( calModel == 0 )
        return;                              // Make sure there is a model to render
        
    //----------------------------------------------------------//
    video::IVideoDriver* driver = SceneManager->getVideoDriver(); // Get the video driver
    CalRenderer* renderer = calModel->getRenderer();            // Get the CalRenderer

    
    
    //----------------------------------------------------------//
    // All we're doing here is form a bridge between the CalRenderer and the IVideoDriver
    // The CalRenderer gives us data (doesn't draw anything) and IVideoDriver needs that data
    // Only problem is that we need to convert it to Irrlicht Compatible data
    // To explain what's going on, this simple diagram should help:
    //  CalRenderer >--GET--> Data >--CONVERT--> Irrlicht Format >--SEND--> IVideoDriver >--DRAW--> ..
    
    //----------------------------------------------------------//
    calModel->getSkeleton()->calculateBoundingBoxes();        // Calculate the bounding box of the skeleton
    
    //----------------------------------------------------------//
    if ( renderer == 0  )
        return;                               // Bail out if no renderer was received
    if ( !renderer->beginRendering() )
        return;                  // Bail out if renderer encountered an error
        
    //----------------------------------------------------------// Move to our position (and rotate/scale)
    driver->setTransform( video::ETS_WORLD, AbsoluteTransformation );
    
    
    //----------------------------------------------------------//
    s32 numMeshes = renderer->getMeshCount();                   // Get the number of meshes we need to draw
    for ( s32 meshId = 0; meshId < numMeshes; meshId++ )        // Loop for every mesh
    {
        //--------------------------------------------------------//
        s32 numSubMeshes = renderer->getSubmeshCount(meshId);     // Get the number of submeshes
        for ( s32 subId = 0; subId < numSubMeshes; subId++ )      // Loop for every submesh
        {
            if ( !renderer->selectMeshSubmesh(meshId, subId) )      // Select the current mesh and submesh
            {
                continue;                                             // Skip this submesh if it failed
            }
            
            //------------------------------------------------------//
            if ( !OverrideMaterial )                              // Should we use Cal3D's material?
            {
                u8 meshColor [4];                                     // Color stored in RGBA format
                // Irrlicht wants it in ARGB format
                renderer->getAmbientColor( meshColor );               // Get the ambient color
                Material.AmbientColor.setRed( meshColor[0] );       // Set the red component
                Material.AmbientColor.setGreen( meshColor[1] );     // Set the green component
                Material.AmbientColor.setBlue( meshColor[2] );      // Set the blue component
                Material.AmbientColor.setAlpha( meshColor[3] );     // Set the alpha component
                
                renderer->getDiffuseColor( meshColor );               // Get the diffuse color
                Material.DiffuseColor.setRed( meshColor[0] );       // Set the red component
                Material.DiffuseColor.setGreen( meshColor[1] );     // Set the green component
                Material.DiffuseColor.setBlue( meshColor[2] );      // Set the blue component
                Material.DiffuseColor.setAlpha( meshColor[3] );     // Set the alpha component
                
                renderer->getSpecularColor( meshColor );              // Get the specular color
                Material.SpecularColor.setRed( meshColor[0] );      // Set the red component
                Material.SpecularColor.setGreen( meshColor[1] );    // Set the green component
                Material.SpecularColor.setBlue( meshColor[2] );     // Set the blue component
                Material.SpecularColor.setAlpha( meshColor[3] );    // Set the alpha component
                
                Material.Shininess = renderer->getShininess();      // Set the shininess factor
                
                if ( renderer->getMapCount() >= 1 )
                {                                                     // Get the irrlicht texture from user data
                    Material.setTexture(0, (video::ITexture*)renderer->getMapUserData(0));
                }
            }
            
            //------------------------------------------------------//
            s32 vertexCount = renderer->getVertexCount();           // Get the number of vertices
            if (vertexCount == 0)
                continue;                         // Skip if the mesh is empty
                
            static core::array<core::vector3df> vertexBuffer;    // Use a core::array to support msvc
            vertexBuffer.set_used( vertexCount );          // Make room for the vertex coordinates
            renderer->getVertices( &vertexBuffer[0].X );              // Copy the vertices into the buffer
            
            //------------------------------------------------------//
            static core::array<core::vector3df> normalBuffer;
            normalBuffer.set_used( vertexCount );       // Buffer for the vertex normals
            renderer->getNormals( &normalBuffer[0].X );               // Copy the normals to the buffer
            
            //------------------------------------------------------//
            static core::array<core::vector2df> texCoordBuffer;
            texCoordBuffer.set_used( vertexCount );                 // Buffer for the vertex texture coordinates
            renderer->getTextureCoordinates( 0, &texCoordBuffer[0].X );// Copy the texture coordinates to the buffer
            
            //------------------------------------------------------//
            s32 faceCount = renderer->getFaceCount();               // Get the number of faces
            static CalIndex cal_indices[30000000];
            renderer->getFaces(  cal_indices );                   // Copy the face indices to the buffer
            static core::array<u16> faceBuffer;
            faceBuffer.set_used( faceCount * 3 );                   // Buffer for the face v1,v2,v3 indices
            for(int i = 0; i < faceCount * 3; ++i)
            {
              faceBuffer[i] = cal_indices[i];
            }
            
            //------------------------------------------------------//
            static core::array<video::S3DVertex> irrVertexBuffer;
            irrVertexBuffer.set_used( vertexCount );                // Buffer for the irrlicht vertices
            for (s32 vert=0; vert<vertexCount; vert++)              // Convert all vertices to irrlicht format
            { // Irrlicht and Cal3D uses different coordinates. Irrlicht's Y points up, where Cal3D's Z points up
                irrVertexBuffer[vert].Pos.X = vertexBuffer[vert].X;  // Set the X coordinate
                irrVertexBuffer[vert].Pos.Y = vertexBuffer[vert].Y;  // Set the Y coordinate (Cal3D's Z coord)
                irrVertexBuffer[vert].Pos.Z = vertexBuffer[vert].Z;  // Set the Z coordinate (Cal3D's Y coord)
                
                irrVertexBuffer[vert].Color.set(255,128,128,128);     // Vertex colors aren't supported by Cal3D
                
                irrVertexBuffer[vert].Normal.X = normalBuffer[vert].X;// Set the X coordinate
                irrVertexBuffer[vert].Normal.Y = normalBuffer[vert].Y;// Set the Y coordinate (Cal3D's Z coord)
                irrVertexBuffer[vert].Normal.Z = normalBuffer[vert].Z;// Set the Z coordinate (Cal3D's Y coord)
                
                irrVertexBuffer[vert].TCoords.X = texCoordBuffer[vert].X;// Set the X texture coordinate (U)
                irrVertexBuffer[vert].TCoords.Y = texCoordBuffer[vert].Y;// Set the Y texture coordinate (V)
            }
            
            //------------------------------------------------------// Invert triangle direction
            for (s32 face=0; face<faceCount; face++)                // Irrlicht wants indices in the opposite order
            {
                u16 faceA = faceBuffer[face*3];                      // Swap first and last vertex index
                faceBuffer[face*3]   = faceBuffer[face*3+2];         // Set the first to the last
                faceBuffer[face*3+2] = faceA;                        // And the last to the first
            }
            
            //------------------------------------------------------// Finally! Time to draw everthing

           /* Material.BackfaceCulling = false; */

           float k;

           if(draw_mode != DM_DEFAULT)
           {
               video::SMaterial debug_material;
               debug_material.Wireframe = true;
               debug_material.BackfaceCulling = false;
               debug_material.Lighting = false;
               driver->setMaterial(debug_material);
              
               /* so that debug looks good for all sizes of models*/
               k = EXTENT_K * BoundingBox.getExtent().getLength();
           }
           else
           {
               driver->setMaterial( Material );
           }

           if(draw_mode == DM_DEFAULT)
           {
               driver->drawIndexedTriangleList(irrVertexBuffer.const_pointer(),
                                               vertexCount,
                                               faceBuffer.const_pointer(),
                                               faceCount);
           }
           else if(draw_mode == DM_WIREFRAME || 
                   draw_mode == DM_WIREFRAME_AND_SKELETON)
           {
               /* draw faces */
               for (s32 face=0; face<faceCount; ++face)
               {
                 u16 i1, i2, i3;
                 i1 = faceBuffer[face*3+0];
                 i2 = faceBuffer[face*3+1];
                 i3 = faceBuffer[face*3+2];

                 driver->draw3DLine(core::vector3df(vertexBuffer[i1].X,
                                                    vertexBuffer[i1].Y,
                                                    vertexBuffer[i1].Z),
                                    core::vector3df(vertexBuffer[i2].X,
                                                    vertexBuffer[i2].Y,
                                                    vertexBuffer[i2].Z),
                                    video::SColor(255,0,0,255));
                 driver->draw3DLine(core::vector3df(vertexBuffer[i2].X,
                                                    vertexBuffer[i2].Y,
                                                    vertexBuffer[i2].Z),
                                    core::vector3df(vertexBuffer[i3].X,
                                                    vertexBuffer[i3].Y,
                                                    vertexBuffer[i3].Z),
                                    video::SColor(255,0,0,255));
                 driver->draw3DLine(core::vector3df(vertexBuffer[i3].X,
                                                    vertexBuffer[i3].Y,
                                                    vertexBuffer[i3].Z),
                                    core::vector3df(vertexBuffer[i1].X,
                                                    vertexBuffer[i1].Y,
                                                    vertexBuffer[i1].Z),
                                    video::SColor(255,0,0,255));
               }

           }

           if(draw_mode == DM_SKELETON || 
              draw_mode == DM_WIREFRAME_AND_SKELETON)
           {
              float lines[1024][2][3];
              int num_lines;
              num_lines =  calModel->getSkeleton()->getBoneLines(&lines[0][0][0]);
              video::S3DVertex vertex;

              for(int line = 0; line < num_lines; ++line)
              {
                  driver->draw3DLine(core::vector3df(lines[line][0][0], 
                                                     lines[line][0][1],
                                                     lines[line][0][2]),
                                     core::vector3df(lines[line][1][0], 
                                                     lines[line][1][1],
                                                     lines[line][1][2]),
                                     video::SColor(255,255,0,0));
                 
                  core::aabbox3df box1(lines[line][0][0]-SKELETON_K*k,
                                       lines[line][0][1]-SKELETON_K*k, 
                                       lines[line][0][2]-SKELETON_K*k,

                                       lines[line][0][0]+SKELETON_K*k, 
                                       lines[line][0][1]+SKELETON_K*k, 
                                       lines[line][0][2]+SKELETON_K*k);

                  core::aabbox3df box2(lines[line][1][0]-SKELETON_K*k,
                                       lines[line][1][1]-SKELETON_K*k, 
                                       lines[line][1][2]-SKELETON_K*k,

                                       lines[line][1][0]+SKELETON_K*k, 
                                       lines[line][1][1]+SKELETON_K*k, 
                                       lines[line][1][2]+SKELETON_K*k);
                 
                  driver->draw3DBox(box1, video::SColor(255,0,255,0));
                  driver->draw3DBox(box2, video::SColor(255,0,255,0));
              }
           }

           if(draw_bbox)
           {
             video::SMaterial debug_material;
             debug_material.Wireframe = true;
             debug_material.BackfaceCulling = false;
             debug_material.Lighting = false;
             driver->setMaterial(debug_material);

             driver->draw3DBox(BoundingBox, video::SColor(255,255,0,255));
           }

           if(draw_normals)
           {
             k = EXTENT_K * BoundingBox.getExtent().getLength();

             video::SMaterial debug_material;
             debug_material.Wireframe = true;
             debug_material.BackfaceCulling = false;
             debug_material.Lighting = false;
             driver->setMaterial(debug_material);

             /* draw normals */
             for (s32 vert=0; vert<vertexCount; ++vert)
             {
                 driver->draw3DLine(core::vector3df(vertexBuffer[vert].X, 
                                                    vertexBuffer[vert].Y,
                                                    vertexBuffer[vert].Z),
                                    core::vector3df(vertexBuffer[vert].X + NORMAL_K*k*normalBuffer[vert].X,
                                                    vertexBuffer[vert].Y + NORMAL_K*k*normalBuffer[vert].Y,
                                                    vertexBuffer[vert].Z + NORMAL_K*k*normalBuffer[vert].Z),
                                    video::SColor(255,0,255,0));
             }
           }
        } // for subId
        
    } // for meshId
    
    //----------------------------------------------------------//
    renderer->endRendering();                                   // Tell the renderer we are finished now
}

void CCal3DSceneNode::OnAnimate( u32 timeMs )
{
    if ( LastUpdateTime > 0 && calModel != 0 )
    {
        calModel->update( (timeMs - LastUpdateTime) * TimeScale / 1000.0f );
    }
    LastUpdateTime = timeMs;
    ISceneNode::OnAnimate( timeMs );
}

CCal3DSceneNode::CCal3DSceneNode( CCal3DModel* model, ISceneNode* parent, ISceneManager* manager, s32 id,
                                  const core::vector3df& position,
                                  const core::vector3df& rotation,
                                  const core::vector3df& scale )
        : ISceneNode( parent, manager, id, position, rotation, scale )
{
    OverrideMaterial = false;
    LastUpdateTime = 0;
    TimeScale = 1.0f;
    
    Model = model;
    
    CalCoreModel* coreModel = 0;
    if ( Model != 0 )
    {
        Model->grab();
        BoundingBox = Model->getBoundingBox();
        coreModel = Model->getCalCoreModel();
    }
    
    if ( coreModel != 0 )
    {
        calModel = new CalModel( coreModel );
        s32 meshCount = coreModel->getCoreMeshCount();
        for ( s32 i=0; i<meshCount; i++ )
        {
            calModel->attachMesh(i);
        }
        calModel->setMaterialSet(0);
        calModel->update(0.0f);
    }
    else
    {
        calModel = 0;
    }

    draw_mode = DM_DEFAULT;
    draw_bbox = false;
}

CCal3DSceneNode::~CCal3DSceneNode()
{
    if ( calModel != 0 )
    {
        delete calModel;
    }
    if ( Model != 0 )
    {
        Model->drop();
    }
}


} // namespace scene
} // namespace irr

