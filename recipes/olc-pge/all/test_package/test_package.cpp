#define OLC_PGE_APPLICATION
#include "olcPixelGameEngine.h"
#include <cstdio>

class Example : public olc::PixelGameEngine {
public:
    Example()
    {
        sAppName = "Conan Test";
    }

public:
    bool OnUserCreate() override
    {
        // Called once at the start, so create things here
        return true;
    }

    bool OnUserUpdate(float fElapsedTime) override
    {
        // called once per frame
        for (int x = 0; x < ScreenWidth(); x++)
            for (int y = 0; y < ScreenHeight(); y++)
                Draw(x, y, olc::Pixel(rand() % 255, rand() % 255, rand() % 255));
        runTime += fElapsedTime;
        return runTime < 1.0f;
    }

    bool OnUserDestroy() override
    {
        std::puts("Finished.");
        return true;
    }
    float runTime = 0.0f;
};

int main()
{
    Example demo;
    if (demo.Construct(256, 240, 4, 4))
        ; // demo.Start();

    return 0;
}
