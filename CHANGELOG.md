# Changelog

## [2.3.1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/compare/v2.3.0...v2.3.1) (2026-04-01)


### Bug Fixes

* remove min-1 and horizon glow from below-horizon rise bar ([fed26f8](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/fed26f86d10a27db2138c59611745bbeb8fd2c01))

## [2.3.0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/compare/v2.2.0...v2.3.0) (2026-03-31)


### Features

* add lunar cycle timeline bar along top row ([72a2566](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/72a25667c193afd468e1d3ad4832a1147434f44b))

## [2.2.0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/compare/v2.1.2...v2.2.0) (2026-03-31)


### Features

* add event countdown label to moon display ([6347910](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6347910937c2312ef491196eddc977d676c743a5))

## [2.1.2](https://github.com/d0ugal/iDotMatrix-HomeAssistant/compare/v2.1.1...v2.1.2) (2026-03-31)


### Bug Fixes

* use pure black background to avoid RGB565 blue quantization artefact ([624dd55](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/624dd55c77a92bb9118d164c61e6384edc599c04))

## [2.1.1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/compare/v2.1.0...v2.1.1) (2026-03-31)


### Bug Fixes

* cap display text at 20 chars with ellipsis ([352e15d](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/352e15dbf12962c4b37ffc3237a25f97dd5fb99c))


### Performance Improvements

* reduce now-playing GIF size for reliable BLE transfer ([6403945](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/640394564f4a20246cc976c3beed5f174b691379))

## [2.1.0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/compare/v2.0.0...v2.1.0) (2026-03-30)


### Features

* Add `bleak-retry-connector` dependency and implement robust BLE connection retries with error handling. ([47e3c1b](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/47e3c1b892983d886b855a955c74b1b48274e93f))
* Add advanced display mode with layered text and image rendering, configurable via a new Lovelace UI card. ([458f33c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/458f33cc9315be3487102e570ef0fff1570f2f46))
* Add autosize (perfect fit) switch and implement dynamic font sizing with centering for text rendering. ([7f0a17c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/7f0a17ca07f378b99cdb1ea2261f40f48961b1e9))
* add BLE connected, screen on/off, and last render sensors ([2e9ff5c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/2e9ff5c29e41c708a8fba25168e3a4cdf188dca7))
* Add blur/sharpness control for text layers with corresponding UI and backend rendering logic. ([6c5e9b0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6c5e9b0879f0f76e4179cf20b11d7230a6a2fb14))
* Add carousel interval support decoded from BLE capture ([f0712a9](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/f0712a963916b32bb47a9b663b752d7dab39300b))
* add display_emoji service using Twemoji ([18b0a9d](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/18b0a9d7b429aac676c7111711bce55c95a6e15a))
* Add display_gif service for animated GIF support ([ddb6118](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/ddb611820d0d2a1017d4c4682cd3aa732b170119))
* add DISPLAY_MODE_MOON with built-in moon phase renderer ([1984efb](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/1984efb970cb927061b2b084263899b8960b7888))
* Add dynamic font loading from backend service to frontend UI. ([6fcb1b3](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6fcb1b3d9c9101ab9a0d42f9a964dd780fbd8e5d))
* Add font size and font selection to the iDotMatrix card UI. ([a67bf6f](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a67bf6fbfdb471b11115897e2e8c042736ff4d25))
* add now_playing service with album art, pixel-font overlay, auto-revert to moon ([ff8225e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/ff8225e1b0858493593369a6ebf0e1e0e24feec5))
* Add per-GIF retry logic for flaky Bluetooth ([30aae06](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/30aae06f9ae8d4bd2852e9a6df0ddb02e441f46f))
* Add persistent storage for iDotMatrix settings and a development environment setup script. ([dee0009](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/dee0009d381e6f8a0ed842fbf4ad3949ec9c7436))
* Add robust error handling for GIF rotation ([7918118](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/791811812dc91429c446cecbd47873cfe8ab18e9))
* add screen_on and screen_off services ([b90efdf](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/b90efdf7ae214ad894c8de50527bb7fa1e73d7b4))
* add send_image service for pre-rendered PNG upload ([0900c26](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/0900c2659c8edf6c4ff680abb68722c27e483cf5))
* Add trigger entity selection to the UI and backend for explicit state change-based updates. ([1c1d53e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/1c1d53e7e04c31b8c745aa5a3e1fccd7752ae1d6))
* Added Pixel Fonts (VT323, Press Start 2P) ([346563e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/346563e1fcfd58eb48e1c52613f053ef7c62d728))
* Advanced Text Options (Fonts, Animation, Speed, Color) ([e3ebf26](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/e3ebf26d597b7d549c62d5f7f4181ebc7ef9141b))
* Allow Negative Spacing and Fix Multiline Logic ([d9fdf39](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/d9fdf39eb68fda329ebd4435a628ae52a87ea294))
* animated scrolling text for now_playing when track/artist overflows ([c8e1107](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/c8e1107322a8f8e4f224fd2d8dab11d40ea889dc))
* Asynchronously scan for available fonts during setup and pass them to the font selection entity. ([a2fd0f1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a2fd0f1537a2c349b64fdbb641a2662f3d8ebc23))
* cache now_playing GIFs to disk by track/artist/art hash ([a779006](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a779006ff8dfe5307d09123c5bbe799c70175841))
* Clock Date, 24h Format, and Live Color Updates ([9f446b0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/9f446b0f7b7e84a8299fff19816f6daa09c1dc95))
* Enhance Bluetooth connection reliability by polling for devices and refactor font scanning to be asynchronous. ([b4b3ac2](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/b4b3ac2df9c90e8a40caab3ff6101e21860db8ec))
* implement backend storage and UI for saving, loading, and deleting iDotMatrix designs. ([d5e1e1a](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/d5e1e1a32f38f22c270d6511f57f1f784f8bd498))
* Implement Fun Text entity for animated word display with a configurable delay. Wohooo ([6a9fbd0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6a9fbd0c7bc2542a3b68c4a48219037ba3b642ca))
* Implement iDotMatrix face designer UI with multi-layer support, Jinja templates, entity tracking, and automatic display updates. ([e1d34c3](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/e1d34c3fecc60863ee073ba726b254e298d61cd6))
* Implement Lovelace card resource cache busting with versioning and enhance config flow with error handling and a Bluetooth discovery confirmation step. ([6f67a56](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6f67a560e57d41a100c21702f515fe660cb8dcc7))
* Implement server-side face preview rendering and add design save/load functionality with spacing controls to the card. ([8a5c225](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/8a5c2253742072aec4be544234e95566438f19ba))
* Integrate Home Assistant's Bluetooth stack for proxy support in the connection manager. ([a7abf7c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a7abf7cebc94edf03d69b9ce51a30273cf7e5f6b))
* Match Android app BLE protocol from HCI snoop analysis ([d7bac28](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/d7bac286fdba6f82e01ae5f6f95a0db76d92c977))
* Migrate frontend service calls to WebSocket, add character spacing for text layers, and offload image saving to an executor. ([4e3b4a7](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/4e3b4a78aeb6ab6f915456f5bc80a676975c0891))
* Multiline Text Mode and Screen Size Selection ([4330d76](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/4330d76dbdce167066df86675ea7abbb354aa031))
* overhaul — strip to moon/now_playing/image display with light entity ([e0b4a2e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/e0b4a2e61992424a4e49e0b72cb6f54aa84e8697))
* Panel Colour Light Entity and Brightness Control, Multiline Text ([32be9c1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/32be9c1839a160ab8b11baf3874f6037d4344e8c))
* Pixel Perfect Bitmap Font Support (.bdf) ([9893160](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/9893160f511c9a1accb107c727125a4e6bac4404))
* Proportional Text Spacing and Spacing Control ([c8e2e90](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/c8e2e90332af5fc1766be7cddb2c7d17a3ccc1fa))
* Randomize GIF rotation order ([8b4d44d](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/8b4d44d1d9178bf65c27ae49499bda5e80c18806))
* Text Blur/Sharpness Control ([bb09026](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/bb090264f3796ec3d24fbdf328b290ae2602068e))
* Text Font Size Control ([c790f45](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/c790f45903f330163a65c985fc7329ce999d6f86))
* Update clock and time settings to new client API, fix clock import typo, and add Home Assistant development script. ([dedaa23](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/dedaa23743060d737c484fe97043648d739c37f0))
* upload moon as single-frame GIF for persistence through BLE disconnect ([e5ee5b4](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/e5ee5b4ff0d3dd79fb5b06216887fdf35d7a5e78))
* Vertical Spacing Control and Spacing Labels ([c6909d0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/c6909d0407df2a46351a03985d2f156cfcd570a1))


### Bug Fixes

* Add 100ms delay between payload chunks for proxy flow control ([5091e0e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/5091e0edc13b457a405bc2facbaed3d4cebeade7))
* Add 10ms delay between BLE writes for flow control ([a47e188](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a47e18827dd1b74edef1057e08302a2f70168409))
* add DISPLAY_MODE_EXTERNAL to stop coordinator overwriting send_image with clock ([cb5bf90](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/cb5bf902dc3d997b40160fa73221ffc9296b203e))
* add packages wrapper to release-please config ([a5551c0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a5551c09e1271482f7ece3bc379952143590ac87))
* Avoid blocking I/O in async event loop for GIF operations ([42f4967](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/42f4967a066509e83f0243c497131ebeefec9a70))
* Bluetooth discovery crash and device listing ([ef5046b](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/ef5046be6d7468eba47f52d3895ca7dd83a19223))
* check setMode/uploadUnprocessed return values, log real failures ([9e751b1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/9e751b12a4f0f4d98d2b8bb9cb0d395f58897d83))
* Clear screen before each GIF upload ([48d4b26](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/48d4b26b51b7c545aa861b4b0094775140cbf465))
* Config flow entry data key mismatch (CONF_MAC) ([bb0986b](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/bb0986be002ff70a8fae4bb76707111f715f8594))
* correct type errors in vendored client library ([2f9af3e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/2f9af3e370b8c53d1e19489e18a673b6eff8d3eb))
* correct upstream licence from MIT to GPL v3 in README ([30fc47a](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/30fc47a16d737d32e10c6e11dbcb2d7840f07d64))
* don't update default when display_for is set ([440557c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/440557cc8a38412d03ab7d7b7e73ddcfb5f3cf78))
* Duplicate devices (unique_id) and Text entity AttributeError ([ebf3af0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/ebf3af0edd5972fdadcadc1baf630dd8eeac40ec))
* Enable DIY Mode for Multiline Text ([88c4d3e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/88c4d3e0889a3a2a6fe400abbc57204b91dd2d3c))
* exclude client library from pyright (upstream type errors) ([a37d729](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/a37d7294c3e2f86675ad9dce42a31295a01aa654))
* Exit batch mode before single GIF upload ([8d2888c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/8d2888cb5c894de910c7bb157554585cabbd2985))
* fall back to github.token when RELEASE_TOKEN is not set ([ca089c7](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/ca089c7acf510786aa96e5c2d668f7bcf5ff1cc3))
* force reconnect and retry on GIF upload failure ([48431e5](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/48431e5ee533a8e0470b5a3e495f195fed989244))
* Handle LovelaceData API change in Home Assistant ([29521f1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/29521f14f2548d133e326bfa0526cb7f4bc87d07))
* ImportError in select.py (missing EntityCategory) ([7e55c57](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/7e55c57b4ea116b2460602c0e4230c1aeff051e4))
* log moon render success at INFO level ([2f35b8c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/2f35b8cab22e5db38d7b3aaf64a8ba36d6115f0e))
* log send_image failures and BLE send when not connected ([37d8a81](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/37d8a818dcbcb10a1fe9e3ff8d1b9c15566e080d))
* Loop GIFs infinitely and revert batch disable ([45acece](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/45acecefadd08dd04d71fdb62aa80dc2f33fb5fa))
* Missing CONF_MAC import in __init__ ([798f9b6](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/798f9b64ab88012657e02e75d8b881ab65013e03))
* Move manifest.json read to executor to avoid blocking event loop ([45cd338](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/45cd338807b4abcd1ab1a620bad56a9883534cd8))
* Pixel-perfect Multiline Text Wrapping and Spacing Support ([e9b00f2](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/e9b00f25d12ebb7b4735cbe6e845fff302f1f6f5))
* re-render moon immediately after integration reload ([f9eb09f](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/f9eb09f8df55cec8ab5962842f5fd52e548a773d))
* Reduce GIF upload logging from info to debug ([4e2a443](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/4e2a44373f9dc433569addd93d4474df07880181))
* reduce moon refresh to 30s to prevent BLE proxy timeout blanking display ([1d9fab3](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/1d9fab31d94328a15c9db44ff9ae37d5c1e456e8))
* remove deleted module imports from client/modules/__init__.py ([9098eb1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/9098eb1a6fec3af5dcdd99117d743ebab5950a37))
* remove invalid SensorDeviceClass.CONNECTIVITY (use BinarySensorDeviceClass) ([6d18e2a](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6d18e2a5ee4536474a6abeecb9b7f4cd61219bec))
* Remove screen clear before GIF upload ([2dad86e](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/2dad86e5c0db8878fa9c564961c01fe8525dde22))
* Replace absolute imports with relative imports in client lib ([c641bb4](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/c641bb4fc739a6a69d9fe08b4f2c23fa70404260))
* Replace blocking time.sleep with await asyncio.sleep ([22aeed7](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/22aeed71ff690135b36e2f960a89f4d4ca7c670b))
* Route all GIF uploads through batch protocol ([4cc9a81](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/4cc9a81d143cbdb0ef8de0a6c8a069a88b4c0714))
* Select entity AttributeError ([25ea100](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/25ea1003086a137fb1f390c0bfda0c3e4891fcc1))
* skip now_playing display when entity has no artwork or metadata ([991f0f3](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/991f0f3517cd0f5a1ccc66faa80b674d8d33d7f2))
* suppress false-positive pyright errors from missing HA stubs ([4bc9f52](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/4bc9f52539011d63c30d55e30d801a9f28dfb812))
* Text entity crash - Resolve absolute font path ([2955459](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/29554595054d7d46a0bdbcc3071c7abf6d1930dd))
* Thread-safe Lovelace resource registration ([4dd2cd0](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/4dd2cd0bbf1667a1a9bb00298a20050ae485f548))
* Use BLE Write Request for reliable GIF uploads through proxy ([46e294c](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/46e294cf1cc249fca9518e3aee67fab02358ab32))


### Documentation

* add Buy Me A Coffee badge to README ([1c68ea1](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/1c68ea1f17bbd495b183627acbb8cb7f91705764))
* add DEBUGGING.md for moon display mode ([478d105](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/478d105e89e8cfc3e84c6395b3f27b60aa828f6b))
* Add GIF animation guide and BLE proxy tips to README ([6584425](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/6584425adf15f1aa254a4095ba4fd53c7b55d20b))
* Add HACS Custom Repo instructions and WIP Warning ([edb0cde](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/edb0cdee2613514b10f5a8800147c902672d9c9c))
* Add real-world automation examples for GIF rotation ([e4202b2](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/e4202b2e8f690d08c948b9b14564da5a4183c995))
* document raw image vs GIF persistence behaviour ([41fec79](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/41fec79d48b21d43b8ebd47ed62a2d05112fa89c))
* rewrite README and update manifest for fork identity ([72b3479](https://github.com/d0ugal/iDotMatrix-HomeAssistant/commit/72b3479bef48720b20f1588e051bb0ab1a01815e))
