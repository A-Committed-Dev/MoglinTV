# MoglinTV - Your Friend When You Have None Left :)

Are you also still consumed by childhood, rocking the same game every weekend like when you were a child?
Is your friends list also deserted like mine?

<img src="https://github.com/A-Committed-Dev/MoglinTV/blob/main/images/nofriends.png" alt="Alt Text" width="400" height="500">

Fear not, I got the solution for you!

# Introducing MoglinTV
MoglinTV is your real-life desktop companion that will accompany you through all of your adventures in Lore.

<img src="https://github.com/A-Committed-Dev/MoglinTV/blob/main/images/moglintv.jpg" alt="Alt Text" width="600" height="600">

He features:
- Absolutely adorableness
- Companionship
- 5 whole inches of face
- A wiggly waggly tail
- A very weak brain stem
- Game integration
- 8GB RAM (EXPENSIVE!)
- A very good listener but not much of a talker
- Built-in charpage viewer

MoglinTV is what happens when you don't tell your furry moglin baby not to sit too close to the TV, and therefore he is destined for only desktop adventures.

# Technical Stuff.. For Nerds

I built MoglinTV by composing him of 3 parts (I know you didn't sign up for Moglin Anatomy 101 but here we are):

1. **Faces Container** - A Flask web server hosting his animated face expressions and a charpage proxy, served to a 5" display via Chromium in kiosk mode.
2. **Hardware Container** - The brain that drives the SG90 tail servo via hardware PWM, reads the ADXL335 accelerometer through an ADS1115 ADC over I2C, and decides his mood based on physical interactions (shakes, flips).
3. **Game Client** - A desktop-side Python script that watches your AQW game window using screen capture (`grim` on Wayland + `hyprctl` for window geometry *iknow linux user.. I use arch btw*), then runs OpenCV Canny edge detection and template matching to detect when you croak. It posts the bad news to the hardware container over HTTP.

All three parts communicate over HTTP. The two containers run on the Raspberry Pi via Docker Compose, while the game client runs on your desktop PC.
```
┌─────────────────┐       HTTP POST        ┌─────────────────────┐      HTTP POST        ┌─────────────────┐
│   Game Client   │ ───────────────────▶   │ Hardware Container  │ ────────────────────▶ │ Faces Container │
│   (Desktop PC)  │         death          │   (Raspberry Pi)    │     mood updates      │  (Raspberry Pi) │
│                 │                        │                     │                       │                 │
│ • Screen capture│                        │ • SG90 servo        │                       │ • Flask server  │
│ • OpenCV edge   │                        │ • ADXL335 accel     │                       │ • 8 face moods  │
│   detection     │                        │ • ADS1115 ADC       │                       │ • Charpage proxy│
│ • Template match│                        │ • Mood state machine│                       │ • SSE streaming │
└─────────────────┘                        └─────────────────────┘                       └─────────────────┘
                                                    ▲                                          │
                                                    │ HTTP POST (tap/interact)                 │
                                                    └──────────────────────────────────────────┘
                                                              Chromium kiosk on 5" screen
```

### How Death Detection Works

The game client captures the AQW window using `grim`, converts the frame to grayscale, runs Canny edge detection on both the captured frame and a pre-made death screen template, then uses template matching to find a match. If confidence is sufficent, it's a confirmed croak. The death counter resets after 10 minutes of not dying (optimistic, I know).

<img src="https://github.com/A-Committed-Dev/MoglinTV/blob/main/game/debug_edges.png" alt="Alt Text" width="600" height="600">

### The Charpage Proxy

The faces container includes a Flask Blueprint that proxies AQW character pages from `account.aq.com`. It rewrites the Flash SWF embed URLs so they load through a local proxy (bypassing CORS), then serves the whole thing via [Ruffle](https://ruffle.rs/)  a Flash emulator  scaled to fit the 5" display. Tap the screen and hit the charpage icon to admire yourself instead of the moglin's face.


## The Moglin Guts :/

- **Brain** — Raspberry Pi 5 with 8GB of RAM (he's not cheap to feed)
- **Face** — 5-inch display running Chromium in kiosk mode over Wayland
- **Tail** — SG90 micro servo (500–2400µs pulse width, 180° range) driven by hardware PWM on GPIO 18
- **Inner ear** — ADXL335 analog accelerometer (300mV/g sensitivity, 1.65V zero-g baseline) wired through an ADS1115 16-bit ADC over I2C (SDA/SCL on GPIO 2/3)
- **Skeleton** — All "neatly" soldered to a prototype board and stuffed inside a 3D-printed moglin skinsuit

<img src="https://github.com/A-Committed-Dev/MoglinTV/blob/main/images/guts.jpg" alt="Alt Text" width="600" height="600">


# Interactions of the silly desktop moglin

MoglinTV has many different interactions. For starters, when you first meet him he will probably be sleeping (he's very lazy).

![alt text](https://github.com/A-Committed-Dev/MoglinTV/blob/main/images/tap.gif)

But you can tap to wake him up, which in turn will make him very happy to see you, and occasionally he will wiggle his tail for you. He's also very sympathetic so if you accidentally croaked in game, he would mourn you for some time. But you'd probably see that if you continue to croak a lot consecutively, he might not be so sympathetic. And if you then were to get your frustrations out on him by shaking him, he might not be so happy with that. And if you for some reason felt that you wanted to turn him upside down, remember he has a very weak brain stem so don't do it for too long...


If you get tired of looking at his face and would rather look at something prettier, like yourself, tap the screen and click the charpage icon. Do the same to return to your square friend.
  
![alt text](https://github.com/A-Committed-Dev/MoglinTV/blob/main/images/charpage.gif)


For all of the features, go see my submission for the Everything Goes contest!

# My submission to the Everything goes contest!

will come here soon!

# Tribute to the awesome team at artix entertianment 

I built MoglinTV as part of the Everything Goes contest, something which I normally don't participate in. But Adventure Quest Worlds has been a huge part of my life and online history, it's part of the reason I have pursued computer science and robotics. For that, a huge thanks for being awesome and creating awesome stuff. It has made a difference.

Keep being awesome and I will do the same!

Farewell, see you around Battleon — Fern
