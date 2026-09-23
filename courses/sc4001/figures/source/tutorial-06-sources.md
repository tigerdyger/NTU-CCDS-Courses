# SC4001 Tutorial 06 figure provenance

Source: `tute6_ans.pdf`, SC4001 Tutorial 6 reference solutions, *Convolutional Neural Networks* (24 PDF pages). Page numbers are one-based.

These six assets are embedded images extracted with pypdf and saved losslessly as PNG. No plots were reconstructed, no values or axes changed, and no complete slides are included. They support the adjacent explanations and critical discussion in `tutorial-06.tex`; they are reference experiments, not independently rerun training results.

| Asset | Page | Embedded image | Dimensions | Purpose |
| --- | --- | --- | --- | --- |
| `tutorial-06-rgb-conv.png` | 15 | Image70.jp2 | 349 x 136 | Compare original RGB image and two convolution outputs. |
| `tutorial-06-filters.png` | 23 | Image106.png | 493 x 387 | Distinguish learned weights from activations. |
| `tutorial-06-conv-maps.png` | 22 | Image102.png | 491 x 390 | Show 25 convolution maps for digit 9. |
| `tutorial-06-pool-maps.png` | 22 | Image103.png | 498 x 389 | Explain spatial downsampling without changing channel count. |
| `tutorial-06-sgd.png` | 24 | Image95.png | 640 x 431 | Baseline test-accuracy curve. |
| `tutorial-06-momentum-decay.png` | 24 | Image110.png | 640 x 434 | Compare joint decay/momentum run; axis limits differ from baseline. |

The first image retains its limited source resolution. Embedded feature-image montages do not specify absolute intensity scales. Curve values in the notes are approximate visual readings, not raw logs. This limited educational/commentary use does not establish permission to redistribute the full teaching materials or transfer ownership of the figures; review before public publication.

Source SHA-256: `30b8211e2b11ae07b61868003226d60afa9f0eef1707720f42c275b42bc0afd5`.

Asset SHA-256 values:

```text
e7d30b2499218f50f7bd37cfed0bd8b7f017221ebd035bd12ebbe2ef54c775a1  tutorial-06-rgb-conv.png
ee1973064c3a2df01d50185ec2d0a2c17487b220d95325fc94fdccab5fd1780a  tutorial-06-filters.png
f2a38dc16ffaf920442f504e57c9da947350b040ce839908c830e159bc45b864  tutorial-06-conv-maps.png
40b2e0927d9966537f5622c7ba4fc87e106b5fddf319db451a1137b0b5bece72  tutorial-06-pool-maps.png
f542466b86a7842516908daba2e546f5f24bd70f1c47b14b5152b3c139aad220  tutorial-06-sgd.png
eb885b856d4178aa5bff136f208bc130c200369c8295c9b4f8a3f96299ef22d1  tutorial-06-momentum-decay.png
```
