CC=g++
CFLAGS=-c -Wall
LDFLAGS=
SOURCES=CountSocialTieMain2.cpp Util.cpp NetworkDAta.cpp
OBJECTS=$(SOURCES:.cpp=.o)
EXECUTABLE=main

all: $(SOURCES) $(EXECUTABLE)
	
$(EXECUTABLE): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.cpp.o:
	$(CC) $(CFLAGS) $< -o $@

