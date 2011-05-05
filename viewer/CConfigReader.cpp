#include "CConfigReader.h"

#include <stdlib.h> // included for atof and atoi

//#define DEBUG_CONFIG

#ifdef DEBUG_CONFIG
  #include <iostream>
  using namespace std;
#endif

//============================================================//
float CConfigReader::getConfigValueAsFloat() const
{
  return atof( m_CfgValue );
}

//============================================================//
int CConfigReader::getConfigValueAsInt() const
{
  return atoi( m_CfgValue );
}

//============================================================//
bool CConfigReader::nextConfig()
{
  m_CfgName = 0;
  m_CfgValue = 0;

  //----------------------------------------------------------//
  Start:                                                      // Going back here will go to the next line

  if ( !m_File.good() ) return false;
  
  #ifdef DEBUG_CONFIG
    cout << "Loading line.." << endl;
  #endif
  
  std::getline( m_File, m_Buffer );                           // Copy the next line into the buffer
  
  #ifdef DEBUG_CONFIG
    cout << "Loaded line: " << m_Buffer << endl;
  #endif
  
  const char* c = m_Buffer.c_str();                             // Make a pointer to iterate the file
  const char* bufferStart = c;                                  // Remember the start of the buffer
  
  //----------------------------------------------------------// Find the beginning of the first word
  while ( *c == ' ' || *c == '\t' || *c == '#' || *c == '\n' || *c == 0 )
  {                                                           // Walk past all the whitespace
    if ( *c == 0 ) goto Start;                                // Skip this line (it is empty)
    if ( *c == '#' ) goto Start;                              // Skip this line (it is a comment)
    if ( *c == '\n' ) goto Start;                             // Skip this line (it is pure whitespace)
    c++;                                                      // Go on to next character
  }
  
  //----------------------------------------------------------// At this point, we have reached the first word
  const char* firstStart = c;                                   // Remember this position
  const char* firstEnd = c;                                     // End of the first word
  
  //----------------------------------------------------------//
  while ( *c != '=' )                                         // Find the equal sign
  {
    //--------------------------------------------------------//
    if ( *c == 0 || *c == '\n' )                              // End of line! This is an error!
    {
      m_Error = ECE_INCOMPLETE_ASSIGNMENT;                    // Set the error
      return false;                                           // Bail out
    }
    
    //--------------------------------------------------------//
    if ( *c != ' ' && *c != '\t' )                            // Is this a character?
    {
      firstEnd = c;                                           // This is the last character so far
    }
    
    c++;                                                      // Go on to the next character
  }

  //----------------------------------------------------------//
  c++;                                                        // Go past the '=' sign
  
  //----------------------------------------------------------//
  const char* secondStart = c;                                  // This is where the second string starts
  const char* secondEnd = c;

  //----------------------------------------------------------// Find the end of second word
  while ( *c != 0 && *c != '\n' )                             // Go to end of line
  {
    if ( *c != ' ' && *c != '\t' )                            // Is this a character?
        secondEnd = c;                                        // This is the last character so far
    c++;                                                      // Next character
  }
  
  //----------------------------------------------------------//
  int index = secondEnd - bufferStart + 1;
  m_Buffer[index] = 0;                                        // Null-terminate at the end of second word
  index = firstEnd - bufferStart + 1;
  m_Buffer[index] = 0;                                        // Null-terminate at end of first word
  
  //----------------------------------------------------------//
  m_CfgName = firstStart;                                     // Set pointer to first word
  m_CfgValue = secondStart;                                   // Set pointer to second word
  
  //----------------------------------------------------------// Everything went OK
  m_Error = ECE_NONE;                                         // No error to report
  return true;                                                // Return true to indicate a config was found
    
}

//============================================================//
CConfigReader::CConfigReader( const char* filename )
{
  m_Error = ECE_NONE;
  m_File.open( filename );
  if ( !m_File.good() )
  {
    m_Error = ECE_NO_FILE;
    #ifdef DEBUG_CONFIG
      cout << "Could not open file \"" << filename << "\"" << endl;
    #endif
  }
}

//============================================================//
CConfigReader::~CConfigReader()
{
  m_File.close();
}
