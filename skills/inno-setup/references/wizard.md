# A branded classic wizard with a silent counterpart

The shipped template enables this layout when the product record supplies `welcomeCredit`, `wizardImage` and `guiExecutable`. Set `silentShortcut` to `create` or `omit` according to the maker's choice. The example credit for Bitcoin Viz was **Brought to you by Lugano's Plan ₿.** and its homepage was `https://plan-b.foundation/bitcoin-viz`. Ask before reusing a sponsor's wording or substituting a repository URL.

| Page | Interaction to verify |
| --- | --- |
| Welcome | The exact credit and logos render. A `TNewLinkLabel` has a tab stop and opens the confirmed HTTPS homepage. Test Tab and Enter in the real wizard. |
| License | The distributed license text appears. Accepting it enables Next. Include the text in the installed stage for unattended installs too. |
| Destination | A Unicode path with spaces works. `DisableProgramGroupPage=yes` and `DisableReadyPage=yes` lead directly to installation. In `CurPageChanged(wpSelectDir)`, set `NextButton.Caption := SetupMessage(msgButtonInstall)` for the localized **Install** caption. |
| Installing | Observe the page transition, successful extraction and installed manifest. |
| Finish | Launch and Start menu are independent checkboxes. A fresh interactive install starts with both clear. On a subsequent interactive run, initialize the shortcut choice from the existing owned link. Apply it when Finish is clicked and remove an unchecked existing link. Both launch paths point to the GUI. |

The template's silent path skips the finish handler. `[Icons]` with `Check: WizardSilent` implements the chosen unattended shortcut default; unattended installs never launch the app. The uninstaller removes the specific shortcut and deletes its group only if empty. Both profiles use the same AppId and different release filenames. [Bitcoin Viz wizard at v0.8.1](https://github.com/LuganoPlanB/bitcoin-viz/blob/v0.8.1/ci/release/installer.iss.in)

## Artwork for ISCC 6.4.3

In the Bitcoin Viz release investigation, a PNG wizard image compiled into Setup and failed to decode when Setup started. A **24-bit Windows BMP** fixed that failure with 6.4.3. Pin and launch the compiler's output when changing image formats. Later compiler documentation can describe different capabilities. [6.4.3 source and documentation](https://github.com/jrsoftware/issrc/tree/is-6_4_3) · [6.4.3 compiler release](https://github.com/jrsoftware/issrc/releases/tag/is-6_4_3)

Keep the original SVGs and a separate derived ICO and BMP. The released panel measures 328 × 628 pixels. The white letters of the color Plan ₿ lockup almost disappeared on off-white. The shipped dark panel keeps the white lettering legible against the orange symbol. Check the rendered welcome and finish pages at the user's display scale, including keyboard focus, wrapping and the distance between the two marks. The fixture saves the rendered welcome window for review. [Original and derived release artwork](https://github.com/LuganoPlanB/bitcoin-viz/tree/v0.8.1/ci/release)

Example regeneration using ImageMagick 7, from a directory containing the two original SVGs. This produces a new composition for visual review. Keep the approved originals and record the converter version and reviewed output hash alongside the project's assets.

```sh
magick -background none bitcoin-roots.svg -trim +repage -resize 150x170 roots.png
magick -background none lugano-plan-b.svg -trim +repage -resize 274x82 lockup.png
magick -size 328x628 xc:'#151c28' roots.png -gravity North -geometry +0+135 -composite \
  lockup.png -gravity South -geometry +0+105 -composite -alpha remove -alpha off \
  -type TrueColor -depth 8 -compress none BMP3:installer-branding.bmp
magick -background none bitcoin-roots.svg -resize 256x256 -gravity Center -extent 256x256 \
  -define icon:auto-resize=256,64,48,32,16 application.ico
```

Check the BMP DIB header for one plane, 24 bits per pixel and BI_RGB compression (zero). An extension change alone does not convert pixel data.
