#!/usr/bin/env python3

import os
import sys
if sys.platform != "darwin":
	print('The script relies on macOS frameworks to create the final, fully sanitized PDF.')
	print('Would you like to omit the last step and produce a PDF suitable for hardcopy printing?')
	
	skipQuartz = input('Enter Y to continue running without the final PDF sanitization step: ') 
	if skipQuartz.upper() != "Y": 
		print('Quitting...')
		quit()
else:
	skipQuartz = 'N'

import subprocess
try:
	import pikepdf
except:
	print('Install pikepdf with "pip3 install pikepdf"')
	quit()

if len(sys.argv) != 3:
	print('Incorrect argument count - expecting 2.')
	print('usage: SANitiSe.py  "FOR420 - Book 1_133769.pdf" "your_SANS_pdf_PASSWORD_goes_HERE"')
	quit()

try:
	print('Performing step 1/2 (hardcopy sanitization)...')
	with pikepdf.open(sys.argv[1], password = sys.argv[2]) as p:
		for page in p.pages:
			for font in page.resources.as_dict()['/Font'].items():
				# Removing "Differences" font definitions which SANS uses to create the watermarks.
				font[1].as_dict()['/Encoding']['/Differences'] = []
		p.save(sys.argv[1][:-4] + '_printable.pdf')
	
	if skipQuartz != 'Y':
		sanitizerCode = '''
// Based on the following code: https://github.com/benwiggy/Swift-PDFSuite/blob/main/scripts/Watermark.swift

import Foundation
import Quartz

func recreatePDF(filepath: String) {
	let pdfURL = URL(fileURLWithPath: filepath)
	if let pdfDoc: PDFDocument = PDFDocument(url: pdfURL) {
		let newFilepath = (filepath as NSString).deletingPathExtension + "_sanitized.pdf"
		let pages = pdfDoc.pageCount
		if let firstPage = pdfDoc.page(at: 0) {
			var mediaBox: CGRect = firstPage.bounds(for: .mediaBox)
			let newURL = URL(fileURLWithPath: newFilepath) as CFURL
			let gc = CGContext(newURL, mediaBox: &mediaBox, nil)!
			for p in (0...pages - 1) {
				let page: PDFPage = pdfDoc.page(at: p)!
				let nsgc = NSGraphicsContext(cgContext: gc, flipped: false)
				NSGraphicsContext.current = nsgc
				gc.beginPDFPage(nil)
				do {
					page.draw(with: .mediaBox, to: gc)
					gc.saveGState()
				}
				gc.endPDFPage()
				if p == pages - 1 {
					NSGraphicsContext.current = nil
					gc.closePDF()
				}
			}
		}
	}
	return
}

if CommandLine.argc == 2 {
	for (index, args) in CommandLine.arguments.enumerated() {
		if index == 1 {
			recreatePDF(filepath: args)
		}
	}
}'''
		with open('sanitize.swift', 'w') as f:
			f.write(sanitizerCode)
		
		try:
			print('Performing step 2/2 (PDF sanitization)...')
			# At this point the watermarks are not visible, but are still present.
			# We use our custom Quartz-based sanitizer to re-create the visible parts of the PDF.
			subprocess.run(['swift', os.path.join(os.getcwd(),'sanitize.swift'), sys.argv[1][:-4] + '_printable.pdf'])
			os.remove(os.path.join(os.getcwd(),'sanitize.swift'))
		except Exception as e:
			os.remove(os.path.join(os.getcwd(),'sanitize.swift'))
			os.remove(sys.argv[1][:-4] + '_printable.pdf')
			print(e)
			print('Failed to create sanitized PDF.')
			quit()
		print('Done.')
	
except pikepdf.PasswordError:
	print('Incorrect password.')
	quit()
except Exception as e:
	print(e)
	quit()