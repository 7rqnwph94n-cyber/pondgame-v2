import AppKit
let output = CommandLine.arguments[1]
let image = NSImage(size: NSSize(width:1024,height:1024))
image.lockFocus()
NSColor(calibratedRed:0.07,green:0.19,blue:0.18,alpha:1).setFill()
NSBezierPath(roundedRect:NSRect(x:32,y:32,width:960,height:960),xRadius:210,yRadius:210).fill()
NSColor(calibratedRed:0.15,green:0.50,blue:0.49,alpha:1).setFill()
NSBezierPath(ovalIn:NSRect(x:140,y:190,width:744,height:540)).fill()
NSColor(calibratedRed:0.69,green:0.85,blue:0.44,alpha:1).setFill()
NSBezierPath(ovalIn:NSRect(x:280,y:420,width:464,height:350)).fill()
NSColor(calibratedRed:0.07,green:0.19,blue:0.18,alpha:1).setFill()
let notch=NSBezierPath(); notch.move(to:NSPoint(x:512,y:585)); notch.line(to:NSPoint(x:775,y:750)); notch.line(to:NSPoint(x:720,y:550)); notch.close(); notch.fill()
let attrs:[NSAttributedString.Key:Any] = [.font:NSFont.systemFont(ofSize:165,weight:.bold),.foregroundColor:NSColor.white]
let title=NSAttributedString(string:"PLAY",attributes:attrs)
title.draw(at:NSPoint(x:280,y:220))
image.unlockFocus()
let rep=NSBitmapImageRep(data:image.tiffRepresentation!)!
try rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:output))
