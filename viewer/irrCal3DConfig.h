#ifndef _IRR_CAL3D_CONFIG_H_
#define _IRR_CAL3D_CONFIG_H_

// This is copied from "platform.h" in the cal3d source code.
// Renamed to IRRCAL3D_API to avoid overlapping names

#if defined(_WIN32) && !defined(__MINGW32__) && !defined(__CYGWIN__)

#ifndef IRRCAL3D_API
#ifdef CAL3D_EXPORTS
#define IRRCAL3D_API __declspec(dllexport)
#else
#define IRRCAL3D_API __declspec(dllimport)
#endif
#endif

#else

#define IRRCAL3D_API

#endif



#endif // _IRR_CAL3D_CONFIG_H_
