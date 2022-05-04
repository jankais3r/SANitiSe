# SANitiSe
Quick introduction into PDF watermarks and how to remove them.


***Disclaimer:** PDF is an [incredibly complex](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf) file format and the only sure way to fully sanitize it is to convert it into some less sophisticated format, e.g. HTML or plaintext. With that out of the way, let's look into one of many potential ways a document can be watermarked.*

Watermarking is a common form of DRM that aims to make the reproduction of copyrighted material either inconvenient or at least traceable back to the source of the original copy. However, like every other form of DRM, watermarks are a major inconvenience primarily for the legitimate, licensed users of the content.

### Custom font encoding within PDF
One of the more curious features of the PDF format is custom font encoding. Besides adjusting individual parameters of used fonts, you can use it to slim down the embedded font files and include only the glyphs contained in your text. Let's say you have an imaginary company called "SANS" and you would like to have your logo rendered in a special font. Custom font encoding allows you to include only the glyphs "S", "A", and "N" and save a lot of space compared to a full font file containing hundreds of different glyphs.

Custom font encoding also allows you to "re-map" the link between characters and glyphs as needed. This can be useful either when you have a custom font with glyphs not corresponding to regular letters, or in case you are attempting some trickery like watermarking a document and you want to make it as difficult as possible to remove your watermark.

These re-mappings are defined in the `Differences` section of the font encoding block and [this post](https://blog.idrsolutions.com/2011/04/understanding-the-pdf-file-format-–-custom-font-encodings/) is a good primer on the topic.


### Practical example
First things first - the most common way a text is stored in PDFs is in zlib/deflate compressed streams (see my [other repo](https://github.com/jankais3r/PDF-Text-Extract) for the most barebones method of PDF text extraction). That means that if you open almost any PDF in a hex editor, you will see chunks of compressed data instead of a readable text.

The most convenient way to inflate the whole file is to use a PDF-manipulation tool like [qpdf](https://github.com/qpdf/qpdf):

`qpdf --stream-data=uncompress document.pdf document_inflated.pdf`

Now that we have an uncompressed PDF file to work with, let's revisit the above-mentioned `Differences` syntax.

How would we encode a simple string like "Welcome to my SANS course"?

First we need to compile a deduplicated list of all used characters, like this:
```
/W /e /l /c /o /m /space /t /y /S /A /N /u /r /s      Ok, now let's assign indexes to the used characters (W=1,e=2, and so on):                                             
01 02 03 04 05 06 07     08 09 10 11 12 13 14 15      And because we work in hex, let's convert those numbers to base16:
01 02 03 04 05 06 07     08 09 0a 0b 0c 0d 0e 0f

That's it, now we know which hex code belongs to which character and we can spell out our original message:
01 02 03 04 05 06 02 07 08 05 07 06 09 07 0a 0b 0c 0a 07 04 05 0d 0e 0f 02
```

An example showing how custom font encoding looks like in a real PDF document:

![hex view](https://github.com/jankais3r/SANitiSe/raw/main/img/hexview.png)


## SANitiSe Setup
1)	Clone this repo to your computer (needs Python 3, preferrably on macOS)
2)	Run `SANitiSe.py  "./path/to/FOR420 - Book 1_133769.pdf" "your_SANS_pdf_PASSWORD_goes_HERE"`
3)	You will receive a decrypted PDF with watermarks removed

If we look at how the script works, we will see two steps:
1) "Hardcopy sanitization" which makes the watermarks transparent by wiping the `Differences` definitions. This is convenient for printing, as the watermarks usually cover part of the content.
2) "PDF sanitization" where the invisible watermarks (and other hidden fingerprints) are removed from the file itself.

The script uses Quartz (bundled with macOS) for the PDF sanitization, so if you use this script on Windows or Linux, you will end up with PDF that still contains transparent watermarks.

![sanitization](https://github.com/jankais3r/SANitiSe/raw/main/img/sanitization.png)

```
Left: Original PDF with watermarks and other hidden fingerprints
                           Middle: Hardcopy-sanitized document with all watermarks transparent
                                                      Right: PDF-sanitized document with all hidden text removed
```
