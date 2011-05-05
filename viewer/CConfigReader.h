#ifndef CCONFIGREADER_H_INCLUDED
#define CCONFIGREADER_H_INCLUDED

/*
  Name: CConfigReader
  Copyright: © 2005
  Author: Asger Feldthaus
  Date: 30-11-05
  Description:  Class used to parse configuration files.
                An example configuration file could look like this:
------------------------------------------------
#
# Configuration file for "Joe Simpson"
#

firstname=Joe
lastname=Simpson
gender=male
age=38

child = Stephan
child = Rachel

-------------------------------------------------

    CConfigReader will parse them from top to bottom.
    getConfigName() will refer to "firstname", "lastname", "gender" and so on
    getConfigValue() will refer to "Joe", "Simpson", "male", etc
    
Hint: Spaces at beginning and ending of line are allowed and will not affect the outcome.
      Likewise, spaces enclosing the '=' sign do not affect the outcome either.
      If a line contains more than one '=' sign (eg. a = b = c), then the output will be:
        "a" = "b = c" (so the name can never contain '=' signs)
    
Example:

CConfigReader reader ( "test.txt" );
while ( reader.nextConfig() )
{
  std::cout << reader.getConfigName() << " is set to " << reader.getConfigValue() << "\n";
}
*/

#include <fstream>
#include <string>

class CConfigReader
{
  public:
    enum E_CONFIG_ERROR
    {
      ECE_NONE=0,
      ECE_NO_FILE,
      ECE_INCOMPLETE_ASSIGNMENT
    };

    CConfigReader( const char* filename );
    ~CConfigReader();

    bool nextConfig();
    
    E_CONFIG_ERROR getError() const
    {
      return m_Error;
    }
    const char* getConfigName() const
    {
      return m_CfgName;
    }
    const char* getConfigValue() const
    {
      return m_CfgValue;
    }
    float getConfigValueAsFloat() const;
    int getConfigValueAsInt() const;
    
  private:
    std::ifstream m_File;
    E_CONFIG_ERROR m_Error;
    
    std::string m_Buffer;

    const char* m_CfgName;
    const char* m_CfgValue;
};

#endif
