#include "CCal3DModel.h"
#include "CConfigReader.h"

#define DEBUG_CAL_MODEL

// Note: Make sure you #define CAL_16BIT_INDICES in "global.h" or in project settings
#include <cal3d/cal3d.h>

namespace irr
{
namespace scene
{

CalCoreModel* CCal3DModel::getCalCoreModel() const
{
    return Model;
}

const core::aabbox3d<f32>& CCal3DModel::getBoundingBox() const
{
    return BoundingBox;
}

s32 CCal3DModel::getAnimationCount() const
{
    return AnimationCount;
}

void CCal3DModel::setAnimationName( s32 animationId, const c8* animationName )
{
    Model->addAnimationName( std::string(animationName), animationId );
}

s32 CCal3DModel::getAnimationId( const c8* animationName ) const
{
    return Model->getCoreAnimationId( std::string( animationName ) );
}


float CCal3DModel::getAnimationDuration(const c8 *animationName) const
{
  return getAnimationDuration( getAnimationId(animationName) );
}


float CCal3DModel::getAnimationDuration(s32 id) const
{
  CalCoreAnimation *core_anim;

  core_anim = Model->getCoreAnimation(id);
  return core_anim->getDuration();
}


const c8* CCal3DModel::getAnimationName(s32 id) const
{
  CalCoreAnimation *core_anim;

  core_anim = Model->getCoreAnimation(id);
  return core_anim->getName().c_str();
}

bool CCal3DModel::loadFromFile( video::IVideoDriver* videoDriver, const c8* filename )
{    
    Model = new CalCoreModel( filename );
    
    CConfigReader reader ( filename );
    
    std::string currentAnimationName = "";
    f32 currentScale = 1.0f;
    s32 animCount = 0;


    predefined_bbox = false;
    
    //----------------------------------------------------------//
    std::string currentPath = filename;                         // Extract the path from the filename
    
    c8* pathBuffer = new c8[ currentPath.size() + 1 ];          // Allocate a buffer for the path
    memcpy( pathBuffer, currentPath.c_str(), currentPath.size()+1 );
    s32 pathIndex = currentPath.size();
    while ( pathIndex >= 0 && pathBuffer[pathIndex] != '\\' && pathBuffer[pathIndex] != '/' )
    {                                                           // Look for the last backslash
        pathIndex--;
    }
    if ( pathIndex >= 0 )                                       // Was a path found?
    {
        pathBuffer[ pathIndex+1 ] = 0;                            // Null the next character
        currentPath = &pathBuffer[0];                             // Use to the path
    }
    else
    {
        currentPath = "";                                         // Use an empty path
    }
    
    delete pathBuffer;
    
    //----------------------------------------------------------//
    core::stringc path = "path";
    core::stringc skeleton = "skeleton";
    core::stringc scale = "scale";
    core::stringc animation = "animation";
    core::stringc mesh = "mesh";
    core::stringc material = "material";
    core::stringc animationname = "animationname";
    core::stringc bbox = "bbox";
    
    #ifdef DEBUG_CAL_MODEL
    
    #ifdef CAL3D_BIG_ENDIAN
        printf("Using big endian\n");
    #else
        printf("Using small endian\n");
    #endif
    
    #endif
    
    s32 result = 1;
    while ( result != -1 && reader.nextConfig() )               // Get each of the configurations
    {                                                           // The Cal3D calls return -1 on error
        //--------------------------------------------------------//
        if ( mesh == reader.getConfigName() )                     // Load a mesh
        {
            #ifdef DEBUG_CAL_MODEL
            printf("Loading mesh \"%s\".. ", reader.getConfigValue());
            #endif
            
            result = Model->loadCoreMesh( currentPath + reader.getConfigValue() );
            
            #ifdef DEBUG_CAL_MODEL
            if ( result == -1 ) printf("Failed!\n");
            else                printf("OK!\n");
            #endif
        }
        
        //--------------------------------------------------------//
        else
        if ( animation == reader.getConfigName() )                // Load an animation
        {
            #ifdef DEBUG_CAL_MODEL
            printf("Loading animation \"%s\".. ", reader.getConfigValue());
            #endif
            
            result = Model->loadCoreAnimation( currentPath + reader.getConfigValue() );
            
            animCount++;                                            // Count number of animations
            if ( result != -1 && currentAnimationName.size() > 0 )  // Assign a name to this animation?
            {
                Model->addAnimationName( currentAnimationName, result );
                currentAnimationName = "";
            }
            
            #ifdef DEBUG_CAL_MODEL
            if ( result == -1 ) printf("Failed!\n");
            else                printf("OK!\n");
            #endif
        }
        
        //--------------------------------------------------------//
        else
        if ( animationname == reader.getConfigName() )            // Set the next animation name
        {
            currentAnimationName = reader.getConfigValue();         // Remember the animation name
        }
        
        //--------------------------------------------------------//
        else
        if ( material == reader.getConfigName() )                 // Load a material
        {
            #ifdef DEBUG_CAL_MODEL
            printf("Loading material \"%s\".. ", reader.getConfigValue());
            #endif
            
            result = Model->loadCoreMaterial( currentPath + reader.getConfigValue() );
            
            #ifdef DEBUG_CAL_MODEL
            if ( result == -1 ) printf("Failed!\n");
            else                printf("OK!\n");
            #endif
        }
        
        //--------------------------------------------------------//
        else
        if ( path == reader.getConfigName() )                     // Set the path
        {
            currentPath = reader.getConfigValue();
        }
        
        //--------------------------------------------------------//
        else
        if ( scale == reader.getConfigName() )                    // Set the scale
        {
            currentScale = reader.getConfigValueAsFloat();
        }
        
        //--------------------------------------------------------//
        else
        if ( skeleton == reader.getConfigName() )                 // Load the skeleton
        {            
            #ifdef DEBUG_CAL_MODEL
            printf("Loading skeleton \"%s\".. ", reader.getConfigValue());
            #endif
            
            result = Model->loadCoreSkeleton( currentPath + reader.getConfigValue() )? 1:-1;
            
            #ifdef DEBUG_CAL_MODEL
            if ( result == -1 ) printf("Failed!\n");
            else                printf("OK!\n");
            #endif
        }
        else
        if (bbox == reader.getConfigName() )
        {
            #ifdef DEBUG_CAL_MODEL
            printf("Loading bbox \"%s\"\n", reader.getConfigValue());
            #endif
           
            core::vector3df min, max;
            predefined_bbox = true;
            sscanf(reader.getConfigValue(), "%f %f %f %f %f %f",
                   &(min.X), &(min.Y), &(min.Z), 
                   &(max.X), &(max.Y), &(max.Z));
            BoundingBox = core::aabbox3d<f32>(min, max);
        }
    }  // while
    
    //--------------------------------------------------------//
    if ( reader.getError() != CConfigReader::ECE_NONE )       // Were there errors in the config file?
    {
        #ifdef DEBUG_CAL_MODEL
        printf("Syntax error in config file \"%s\"\n", filename);
        #endif
        delete Model;
        Model = 0;
        return false;
    }
    
    //--------------------------------------------------------//
    if ( result == -1 )                                       // Were there errors from Cal3D?
    {
        #ifdef DEBUG_CAL_MODEL
        printf("Cal3D could not open one of the files\n");
        printf("Error: %s\n", CalError::getLastErrorDescription().c_str());
        printf("Line: %i in \"%s\"\n", CalError::getLastErrorLine(), CalError::getLastErrorFile().c_str());
        #endif
        delete Model;                                         // Delete the model
        Model = 0;
        return false;                                         
    }
    
    //--------------------------------------------------------// Time to load all the textures we need
    s32 materialCount = Model->getCoreMaterialCount();        // Get the number of materials to load
    for (s32 materialId = 0; materialId < materialCount; materialId++)
    {
        CalCoreMaterial* coreMaterial;
        coreMaterial = Model->getCoreMaterial(materialId);// Get this material
        
        //------------------------------------------------------//
        s32 mapCount = coreMaterial->getMapCount();             // Get the number of maps
        for ( s32 mapId = 0; mapId < mapCount; mapId++)         // Loop through all the maps
        {                                                       // Get the filename of the texture
            std::string mapFilename = coreMaterial->getMapFilename(mapId);
            // Let Irrlicht load the texture
            video::ITexture* texture = videoDriver->getTexture( (currentPath + mapFilename).c_str() );
            // Set a pointer to the texture on the map
            coreMaterial->setMapUserData( mapId, (Cal::UserData)texture );
        } // for mapId
        
    } // for materialId
    
    //--------------------------------------------------------//
    for (s32 materialId = 0; materialId < materialCount; materialId++)
    {
        Model->createCoreMaterialThread( materialId );   // Create a thread for this material
        Model->setCoreMaterialId( materialId, 0, materialId );
    }
    
    //--------------------------------------------------------//
    Model->getCoreSkeleton()->calculateBoundingBoxes( Model );
    
    AnimationCount = animCount;
    
    // Setup the bounding box
    s32 meshCount = Model->getCoreMeshCount();
    //----------------------------------------------------------//
    for ( s32 meshId = 0; meshId < meshCount; meshId++ )
    {
        CalCoreMesh* mesh = Model->getCoreMesh( meshId );
        s32 subCount = mesh->getCoreSubmeshCount();
        
        //--------------------------------------------------------//
        for ( s32 subId = 0; subId < subCount; subId++ )
        {
            CalCoreSubmesh* submesh = mesh->getCoreSubmesh( subId );
            std::vector< CalCoreSubmesh::Vertex >& vertices = submesh->getVectorVertex();

            //------------------------------------------------------//
            if(!predefined_bbox)
            {
                for ( u32 vertId = 0; vertId < vertices.size(); vertId++ )
                {
                    CalCoreSubmesh::Vertex& vert = vertices[ vertId ];    // Swap Z and Y coords due to coordinate system
                    BoundingBox.addInternalPoint( vert.position.x, vert.position.y, vert.position.z );
                } // for vertId
            }
          
        } // for subId

    } // for meshId
    
    // Hooray!!
    return true;
}

CCal3DModel::CCal3DModel()
{
    Model = 0;
    AnimationCount = 0;
}

CCal3DModel::~CCal3DModel()
{
    if ( Model != 0 )
    {
        delete Model;
    }
}


} // namespace scene
} // namespace irr
