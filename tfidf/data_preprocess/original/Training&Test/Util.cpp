#include "Util.h"
#include <sstream>
#include <stdio.h>

#define MAX_BUF_SIZE 655360

vector<string>     Util::ReadFromFile(const char* fileDir)
{
    printf("reading from %s begine\n", fileDir);
    char        buf[MAX_BUF_SIZE];
    char*       eof;
    string      line;

    FILE        *fin = fopen(fileDir, "r");
    vector<string>  res;

    while (true)
    {
        eof = fgets(buf, MAX_BUF_SIZE, fin);
        if (eof == NULL)
            break;
        res.push_back(eof);
    }

    fclose(fin);
    printf("reading from %s done!\n", fileDir);
    return res;
}

string			Util::Int2Str(int num)
{
	string res = "";
	if (num < 0)
	{
		res = "-";
		num *= -1;
	}
	if (num == 0)
		res = "0";
	while (num > 0)
	{
		char d = '0' + (num % 10);
		res = d + res;
		num /= 10;
	}
	return res;
}

string Util::Double2Str(double num){
	std::ostringstream sstream;
	sstream << num;
	std::string varAsString = sstream.str();
	return varAsString;
}

int             Util::String2Int(string str)
{
    int result = 0;
    for (unsigned int i = 0; i < str.length(); i ++)
    {
        if (str[i] >= '0' && str[i] <= '9')
            result = result * 10 + (str[i] - '0');
        else
        {
			if (i == str.length() - 1)
				return result;
            printf("Error when formating string to integer!\n");
            return -1;
        }
    }
    return result;
}

int				Util::TimeCompare(string t1, string t2)
{
	for (unsigned int i = 0; i < t1.length(); i ++)
	{
		if (t1[i] < '0' || t1[i] > '9')
			continue;
		if ((t1[i] - '0') > (t2[i] - '0'))
			return 1;
		if ((t1[i] - '0') < (t2[i] - '0'))
			return -1;
	}
	return 0;
}

vector<string>  Util::StringTokenize(string line)
{
    istringstream   strin(line);
    vector<string>  result;
    string          token;

    while (strin >> token)
        result.push_back(token);

    return result;
}

vector<string>      Util::StringSplit(string line, char separator)
{
    vector<string>  result;
    line += separator;

    int p = 0;
    for (unsigned int i = 0; i < line.length(); i ++)
        if (line[i] == separator)
        {
            if (i - p > 0) result.push_back( line.substr(p, i-p) );
            p = i + 1;
        }

    return result;
}


void Util::SaveToFile(const char* fileDir, char * buffer, long len)
{
	FILE        *fout=fopen(fileDir,"at");
	if (fout ==NULL )
		fout = fopen(fileDir,"w+");
	fseek(fout, 0L ,SEEK_END);
	fwrite(buffer, len , 1 , fout);
	fclose(fout);
}

long Util::StringSplit(char *buffer, long beginning, char separator)
{;
	while (buffer[beginning]	!=	separator)
	{
		beginning++;
	}
	return beginning+1;
}

void Util::LineInsert(FileNode *head, FileNode* newNode)
{
	while (head->next != NULL)
		head = head->next;
	head->next = newNode;
}
long Util::StrToInt(const char*  str, const long beg)
{
	int k = 0;
	int i = beg;
	while (str[i] >='0' && str[i]<='9')
	{
		k = k*10+str[i]-'0';
		i++;
	}
	return k;
}

long  Util:: PosNext(char *buffer, long pos)
{
	pos = StringSplit(buffer,pos,'\n');
	int l = 0;
	l = StrToInt(buffer,pos);
	pos = StringSplit(buffer,pos,'\n');
	
	for (int i =0; i<l; i++)
	{
		pos = StringSplit(buffer, pos, '\n');
		pos = StringSplit(buffer, pos , '\n');
	}
	return pos;	 
}  
bool Util:: IfEnd(char *buffer, long pos)
{
	long k = 0;
	while (buffer[pos] != '\t')
	{
		pos++;
		k++;
		if (k>50)
			return false; 
	}
	return true;
}
