TARGET = viewer

SRC = $(wildcard *.cpp)
OBJS = $(addsuffix .o, $(basename $(SRC)))
CXX = g++
LINK = g++

CXXFLAGS = $(shell pkg-config cal3d --cflags) -g -I/usr/include/irrlicht -I.
LINKFLAGS = $(shell pkg-config cal3d --libs) -lIrrlicht -g


.cpp.o: $< depend
	$(CXX) $(CXXFLAGS) -o $@ -c $<


$(TARGET): $(OBJS) 
	$(LINK) -o $(TARGET) $(OBJS)  $(LINKFLAGS) 


all: $(TARGET)


clean:
	rm -rf $(TARGET) $(OBJS) depend


depend: $(SRC)
	$(CXX) -MM $(CXXFLAGS) $(SRC) > depend



-include depend

