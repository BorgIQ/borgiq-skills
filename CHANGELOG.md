# Changelog

## [0.4.0](https://github.com/BorgIQ/borgiq-skills/compare/borgiq-skills-v0.3.0...borgiq-skills-v0.4.0) (2026-10-02)


### Features

* **borgiq-builder:** current AI models, prices and defaults ([#17](https://github.com/BorgIQ/borgiq-skills/issues/17)) ([ca55302](https://github.com/BorgIQ/borgiq-skills/commit/ca5530286c0640df3e02300c4cbd1a644b782847))
* **borgiq-builder:** document ctx.actor.upstreamActorCount and use it as the forkJoin size ([#20](https://github.com/BorgIQ/borgiq-skills/issues/20)) ([700c2d1](https://github.com/BorgIQ/borgiq-skills/commit/700c2d1206d519a1ed0640d640be4a8f03670016))
* **borgiq-builder:** document custom AI providers, model references and borgiq ai-providers ([#14](https://github.com/BorgIQ/borgiq-skills/issues/14)) ([44b8bba](https://github.com/BorgIQ/borgiq-skills/commit/44b8bba468008be99365036f91a6d3086ef1a13c))
* **borgiq-builder:** document recipes and adding one to a canvas ([#18](https://github.com/BorgIQ/borgiq-skills/issues/18)) ([30b2e08](https://github.com/BorgIQ/borgiq-skills/commit/30b2e08caff1782d89406cffa018122a8d903563))
* **borgiq-builder:** document StreamActor and the streams API ([#6](https://github.com/BorgIQ/borgiq-skills/issues/6)) ([8b22990](https://github.com/BorgIQ/borgiq-skills/commit/8b229905282eb30d116c30f1d1d60cb707e84f4f))
* **borgiq-builder:** document the canvas README (README.md in a bundle) ([#10](https://github.com/BorgIQ/borgiq-skills/issues/10)) ([d83eceb](https://github.com/BorgIQ/borgiq-skills/commit/d83ecebb128ab6093af2eb4b1f13e22106ef3b0b))
* **borgiq-builder:** document the on-delete lifecycle event ([#13](https://github.com/BorgIQ/borgiq-skills/issues/13)) ([f98e22f](https://github.com/BorgIQ/borgiq-skills/commit/f98e22f2a2a210249782c80ca7598a1659a5f8f3))
* **borgiq-builder:** document WebAssembly and blob workers for React apps ([#16](https://github.com/BorgIQ/borgiq-skills/issues/16)) ([0842209](https://github.com/BorgIQ/borgiq-skills/commit/08422092cdb683b5ca3925565261091cd310a054))
* **borgiq-builder:** sync to platform: thinking, code_execution, models ([#12](https://github.com/BorgIQ/borgiq-skills/issues/12)) ([ca23788](https://github.com/BorgIQ/borgiq-skills/commit/ca23788206160502dd0f8fb97a8f36f6d1fae5ec))
* **borgiq-builder:** teach the React app tab title (useTitle, setTitle, title option) ([#54](https://github.com/BorgIQ/borgiq-skills/issues/54)) ([636baae](https://github.com/BorgIQ/borgiq-skills/commit/636baae2ef706a72806696ce78bef3d0b71717f0))
* **borgiq-react-app-builder:** document appSessionId and userId on the app session ([#9](https://github.com/BorgIQ/borgiq-skills/issues/9)) ([e6901bf](https://github.com/BorgIQ/borgiq-skills/commit/e6901bf7d315f8370e6173c4fa7848f2664915b9))
* **borgiq-react-app-builder:** screenshot a built app and set it as its thumbnail ([#15](https://github.com/BorgIQ/borgiq-skills/issues/15)) ([b45ff03](https://github.com/BorgIQ/borgiq-skills/commit/b45ff038ad267b37e6c67042f1414508e138fa81))
* document deployed workspaces and runtime builds ([#5](https://github.com/BorgIQ/borgiq-skills/issues/5)) ([54ba661](https://github.com/BorgIQ/borgiq-skills/commit/54ba6618e3004f556af872dd2c145c22ba5a8e11))
* initial public release of borgiq-skills ([b2cdb75](https://github.com/BorgIQ/borgiq-skills/commit/b2cdb75b5c5f4887979a8d2329a9635a69ffcfba))
* **react-app-builder:** document following a stream with useStreamTail ([#8](https://github.com/BorgIQ/borgiq-skills/issues/8)) ([9385dd6](https://github.com/BorgIQ/borgiq-skills/commit/9385dd60f9df1c30c692d55dc665e47bee19b32f))


### Bug Fixes

* **borgiq-builder:** AI Agent re-applies volumeZipFile when a new run reuses the session ([#21](https://github.com/BorgIQ/borgiq-skills/issues/21)) ([2e5143c](https://github.com/BorgIQ/borgiq-skills/commit/2e5143cbf9e28af15cf9a31d66bc9508f3eefac3))
* **borgiq-builder:** correct agent tool, harness and MCP facts ([#30](https://github.com/BorgIQ/borgiq-skills/issues/30)) ([fc3ae44](https://github.com/BorgIQ/borgiq-skills/commit/fc3ae44db1c533382ab890c8ea58f2de345a8b09))
* **borgiq-builder:** correct code-actor memory, emit and signal semantics ([#31](https://github.com/BorgIQ/borgiq-skills/issues/31)) ([7a81bcc](https://github.com/BorgIQ/borgiq-skills/commit/7a81bccf167dceca783098196e03377c940e03da))
* **borgiq-builder:** correct CollectionActor write, TTL and query semantics ([#27](https://github.com/BorgIQ/borgiq-skills/issues/27)) ([5be8d06](https://github.com/BorgIQ/borgiq-skills/commit/5be8d065d91e12fc22ab0e629ba298775e43c918))
* **borgiq-builder:** correct run, debug and template commands in CLI references ([#35](https://github.com/BorgIQ/borgiq-skills/issues/35)) ([2654129](https://github.com/BorgIQ/borgiq-skills/commit/265412927a61d0b5c1e0e7309003e7e943fb13d3))
* **borgiq-builder:** correct wiring, message-processor and trigger facts ([#33](https://github.com/BorgIQ/borgiq-skills/issues/33)) ([2c54c58](https://github.com/BorgIQ/borgiq-skills/commit/2c54c58ed08bcd62c9edc9577eee34a9c8ba67da))
* **borgiq-builder:** document apiKey / appsAndApiKey webhook levels, meta.user on API-key calls and meta.auth ([#11](https://github.com/BorgIQ/borgiq-skills/issues/11)) ([5bfb795](https://github.com/BorgIQ/borgiq-skills/commit/5bfb795d7968a6a8f7eebb1d2797c3d6a7b1807f))
* **borgiq-builder:** document Server-side credentials as proxy placeholders ([#19](https://github.com/BorgIQ/borgiq-skills/issues/19)) ([f46d77f](https://github.com/BorgIQ/borgiq-skills/commit/f46d77f669cb1c94bc9f984b66ea7b26016fb59b))
* **borgiq-builder:** make the lifecycle commands match the CLI ([#34](https://github.com/BorgIQ/borgiq-skills/issues/34)) ([fa98cd5](https://github.com/BorgIQ/borgiq-skills/commit/fa98cd56692e31e07679389ed8d9cfd1dfe58312))
* **borgiq-builder:** remove internal names from shipped type references ([#22](https://github.com/BorgIQ/borgiq-skills/issues/22)) ([319f5b6](https://github.com/BorgIQ/borgiq-skills/commit/319f5b636f404f35abb41147ea40c812cc615e24))
* **borgiq-builder:** repair reference anchors and check them in CI ([#23](https://github.com/BorgIQ/borgiq-skills/issues/23)) ([ac6e34e](https://github.com/BorgIQ/borgiq-skills/commit/ac6e34e12280325e73ab26b2f654251d0a703aea))
* **borgiq-builder:** support multi-file source for code actors ([#4](https://github.com/BorgIQ/borgiq-skills/issues/4)) ([f9e70e4](https://github.com/BorgIQ/borgiq-skills/commit/f9e70e4bcedb93888563d885cc392cf0215648c0))
* **borgiq-form-builder:** correct component props, page width and viewer access ([#28](https://github.com/BorgIQ/borgiq-skills/issues/28)) ([2d1e377](https://github.com/BorgIQ/borgiq-skills/commit/2d1e37780a351a7a85374899172cb81b48126862))
* **borgiq-react-app-builder:** complete the app scaffold's build setup ([#29](https://github.com/BorgIQ/borgiq-skills/issues/29)) ([60fcdce](https://github.com/BorgIQ/borgiq-skills/commit/60fcdcea9b4aaab64bcea439525420bfa055f363))
* **collections:** add $ system namespace and $meta manifest for discoverability ([#3](https://github.com/BorgIQ/borgiq-skills/issues/3)) ([80a821c](https://github.com/BorgIQ/borgiq-skills/commit/80a821c71a5e63cbe1bfab475f4d60539df7ea42))
* **collections:** mandate single-collection design for app data ([#2](https://github.com/BorgIQ/borgiq-skills/issues/2)) ([eba14d6](https://github.com/BorgIQ/borgiq-skills/commit/eba14d658ee2d677cdccebc6b3712db0f8a6a24f))
* **installer:** never overwrite a skill directory the installer did not create ([#25](https://github.com/BorgIQ/borgiq-skills/issues/25)) ([304648c](https://github.com/BorgIQ/borgiq-skills/commit/304648cc0e0b1f1c2b87b10590da9dc80418e829))


### Refactors

* **borgiq-agent-builder:** matrix as the single decision table; values in references ([#48](https://github.com/BorgIQ/borgiq-skills/issues/48)) ([8365d56](https://github.com/BorgIQ/borgiq-skills/commit/8365d56207fa4598237ced58b6ba331724f70ce1))
* **borgiq-builder:** consolidate CLI references ([#49](https://github.com/BorgIQ/borgiq-skills/issues/49)) ([21adfa8](https://github.com/BorgIQ/borgiq-skills/commit/21adfa88671d05bfec91ccee01b6d4b342662aac))
* **borgiq-builder:** consolidate trigger and flow-actor references ([#45](https://github.com/BorgIQ/borgiq-skills/issues/45)) ([16556a1](https://github.com/BorgIQ/borgiq-skills/commit/16556a1de31d278726c21992277bc13042affdd4))
* **borgiq-builder:** consolidate wiring references; choosing-actors reference ([#42](https://github.com/BorgIQ/borgiq-skills/issues/42)) ([bb96885](https://github.com/BorgIQ/borgiq-skills/commit/bb968853f0e3d277ef416f4d6d40ff25df380422))
* **borgiq-builder:** correct and consolidate the expression context reference ([#46](https://github.com/BorgIQ/borgiq-skills/issues/46)) ([7488e62](https://github.com/BorgIQ/borgiq-skills/commit/7488e627104443e3aa7e77cf455a887ab9e4a2ca))
* **borgiq-builder:** hub holds routing, core rules and a load map ([#51](https://github.com/BorgIQ/borgiq-skills/issues/51)) ([8e0a131](https://github.com/BorgIQ/borgiq-skills/commit/8e0a131851f2781f50e214247c0a983a9dea6ab9))
* **borgiq-builder:** lifecycle commands read the same on every agent ([#52](https://github.com/BorgIQ/borgiq-skills/issues/52)) ([73ed9fd](https://github.com/BorgIQ/borgiq-skills/commit/73ed9fd8bbbd7e6582f66f2844788c1d978fc4ef))
* **borgiq-builder:** merge legacy app references; one thumbnail reference ([#39](https://github.com/BorgIQ/borgiq-skills/issues/39)) ([9a073d0](https://github.com/BorgIQ/borgiq-skills/commit/9a073d05b8997ebea858476d4b8d25096c588634))
* **borgiq-builder:** one generated type reference per module ([#32](https://github.com/BorgIQ/borgiq-skills/issues/32)) ([41542ac](https://github.com/BorgIQ/borgiq-skills/commit/41542ac3d9a49d7744af00e97e22e45fac148237))
* **borgiq-builder:** one home each for AI models, agent tools and the legacy agent ([#47](https://github.com/BorgIQ/borgiq-skills/issues/47)) ([85830c4](https://github.com/BorgIQ/borgiq-skills/commit/85830c44534508e191ee022270b3427ce790a5cf))
* **borgiq-builder:** shared code-actor runtime reference ([#43](https://github.com/BorgIQ/borgiq-skills/issues/43)) ([6f488a6](https://github.com/BorgIQ/borgiq-skills/commit/6f488a6db318d0e51a9efc5cad15a044aad91bf5))
* **borgiq-builder:** split collection references by reader; one home for stream rules ([#40](https://github.com/BorgIQ/borgiq-skills/issues/40)) ([04fe322](https://github.com/BorgIQ/borgiq-skills/commit/04fe32205924d79894065ab79019d3d4767cc638))
* **borgiq-builder:** split interface page references ([#36](https://github.com/BorgIQ/borgiq-skills/issues/36)) ([49a01d6](https://github.com/BorgIQ/borgiq-skills/commit/49a01d68a4df23f2176f345ba3d92864f17a4df1))
* **borgiq-builder:** trim the universal trigger reference ([#44](https://github.com/BorgIQ/borgiq-skills/issues/44)) ([4c77f92](https://github.com/BorgIQ/borgiq-skills/commit/4c77f923a78061645d9bf822e63a9e38ba0d075a))
* **borgiq-form-builder:** read-when table and trimmed decisions ([#37](https://github.com/BorgIQ/borgiq-skills/issues/37)) ([4f0fc08](https://github.com/BorgIQ/borgiq-skills/commit/4f0fc081c377526b6c43c14ce446576d14804966))
* **borgiq-json-schema-builder:** point storage design at collection-design ([#41](https://github.com/BorgIQ/borgiq-skills/issues/41)) ([5a7a351](https://github.com/BorgIQ/borgiq-skills/commit/5a7a35108acdbc40b42cdc8eb2eae5df8a82202c))
* **borgiq-react-app-builder:** move SDK, build and theme detail to references ([#38](https://github.com/BorgIQ/borgiq-skills/issues/38)) ([e222e31](https://github.com/BorgIQ/borgiq-skills/commit/e222e3108e9687e957c9b9edda32a41df8a8a6ee))
