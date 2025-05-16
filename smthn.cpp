#include "SFML/Graphics.hpp"
#include <vector>
#include <cstdlib>

float GRAV_AC = 9.8;
/**
 * @note Logic taken from
 * @cite https://labs.phys.utk.edu/mbreinig/phys221core/modules/m3/Hooke%27s%20law.html
 *
 * @details Some useful functions
 * - Hook's law: F=-kx
 *  - x is the distance from the point of equilibrium (it's natural length) (measured in meters)
 *  - k is the sprint constant which describes the stiffness of the spring (measured in neutons/meter)
 *  - F is the force exerted (towards the equilibrium position) (measured in neutons)
 * - Force function: F=ma
 *  - m is the mass (measured in kilograms)
 *  - a is acceleration (measured in meters/sec^2)
 *  - F is the force produced (measured in neutons)
 * - Acceleration function: a=v/t
 *  - v is the velocity (measured in meters/sec)
 *  - t is the time/delta time (measured in seconds)
 *  - a is the resulting acceleration (measured in meatures/sec^2)
 */

struct Point
{
    sf::Vertex *vertex = nullptr;
    bool locked = false;
};
struct PhysicsObject
{
    sf::Vector2f velocity;
    sf::Vector2f accelertation;
    sf::Vector2f force;
    int mass = 1;
    bool enabled;
};

struct Spring
{
    int length;
    Point *point1 = nullptr;
    Point *point2 = nullptr;
};

struct Simulation
{
    // The updated output points
    std::vector<Point> points;
    // The previous values of the points
    std::vector<Point> previous;
    std::vector<PhysicsObject> physicsPoints;
    sf::VertexArray vertices;
    time_t seed;
    Simulation(int numberOfPoints = 100)
    {
        seed = time(nullptr);
        srand(seed);
        points.resize(numberOfPoints);
        physicsPoints.resize(numberOfPoints);
        vertices.resize(numberOfPoints);
        vertices.setPrimitiveType(sf::Lines);
        // Link the points to their corresponding vertices
        for (int i = 0; i < numberOfPoints; i++)
        {
            points[i].vertex = &vertices[i];
            points[i].vertex->position = sf::Vector2f(((float)rand()) / static_cast<float>(RAND_MAX) * 800.0 + 100.0, ((float)rand()) / static_cast<float>(RAND_MAX) * 800.0 + 100.0);
            int r = ((float)rand()) / static_cast<float>(RAND_MAX) * 256.0;
            int g = ((float)rand()) / static_cast<float>(RAND_MAX) * 256.0;
            int b = ((float)rand()) / static_cast<float>(RAND_MAX) * 256.0;
            points[i].vertex->color = sf::Color(r, g, b);
        }
    }
};
int main()
{
    sf::RenderWindow window(sf::VideoMode(900, 900), "Test window");
    sf::Event event;
    Simulation sim(2);
    while (window.isOpen())
    {
        while (window.pollEvent(event))
        {
            if (event.type == sf::Event::Closed)
            {
                window.close();
                break;
            }
        };
        window.clear();
        window.draw(sim.vertices);
        window.display();
    }
    return 0;
}