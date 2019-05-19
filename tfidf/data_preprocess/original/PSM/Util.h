#pragma once

#include <string>
#include <vector>
#include <map>
#include <set>
#include <utility>
using namespace std;

struct TwoKey 
{
	 char * str;
	 long len;
};

struct FileNode
{
	 char * str;
	 long address;
	 FileNode * next;
};

class   Util
{
public:
	static vector<string>  ReadFromFile( const char* fileDir);
	static vector<string> StringTokenize(string line);
	static int TimeCompare(string t1, string t2);
	static vector<string> StringSplit(string line, char separator);
	static string Int2Str(int num);
	static int String2Int(string str);
	static long StringSplit(char *buffer, long  beginning, char separator); 
	static void LineInsert(FileNode *head, FileNode* newNode);
	static long PosNext( char *buffer, long pos);
	static void SaveToFile(const char* fileDir, char *buffer, long len);
	static long StrToInt(const char * str, const long beg);
	static bool IfEnd(char *buffer, long pos);
	static string Double2Str(double num);

};
