-- build_atlas.lua — Libresprite / Aseprite CLI script
-- Packs every frame of every sprite in sprites/ into a single atlas + JSON.
-- Run:  libresprite -b --script build_atlas.lua

local sprites = app.fs.listFiles("sprites")
local atlas = Image(512, 256, ColorMode.RGBA)
local frames = {}
local x, y, row_h = 0, 0, 32

for _, name in ipairs(sprites) do
  local path = "sprites/" .. name
  local sp = app.open(path)
  for f = 1, #sp.frames do
    app.activeFrame = sp.frames[f]
    local img = Image(sp.spec)
    img:drawSprite(sp, sp.frames[f])
    if x + img.width > atlas.width then x, y = 0, y + row_h end
    atlas:drawImage(img, x, y)
    table.insert(frames, { name = name .. "#" .. f,
                           x = x, y = y, w = img.width, h = img.height,
                           duration = 120 })
    x = x + img.width
  end
  sp:close()
end

atlas:saveAs("atlas.png")
local fh = io.open("atlas.json", "w")
fh:write("{\"frames\": {")
for i, fr in ipairs(frames) do
  if i > 1 then fh:write(",") end
  fh:write(string.format(
    '"%s":{"frame":{"x":%d,"y":%d,"w":%d,"h":%d},"duration":%d}',
    fr.name, fr.x, fr.y, fr.w, fr.h, fr.duration))
end
fh:write("}}")
fh:close()
print("wrote atlas.png + atlas.json, frames=" .. #frames)
