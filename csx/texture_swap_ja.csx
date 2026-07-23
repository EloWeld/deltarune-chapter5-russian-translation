using System;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;

// Универсальная подмена: у каждого локализуемого спрайта spr_X_ja / spr_X_jp
// текстуры кадров указываем на английскую/русскую базу (spr_X либо spr_X_en).
// Так игра показывает не-японский арт, КАК БЫ она спрайт ни выбирала:
//   - через карту scr_84 (scr_84_get_sprite),
//   - прямым присваиванием в коде объекта (sprite_index = spr_X_ja),
//   - в сравнениях (if sprite_index == spr_X_ja) — идентичность ассета сохраняется.
// Запускать ПОСЛЕ import_sprites (тогда базы уже с русским редроу).
// Где EN-источника нет (чисто японские) — пропуск с логом.

var suffix = new Regex("_(ja|jp)$");
int swapped = 0, frames = 0, skipped = 0;

foreach (var s in Data.Sprites.Where(x => suffix.IsMatch(x.Name.Content)).OrderBy(x => x.Name.Content))
{
    string baseName = suffix.Replace(s.Name.Content, "");
    var src = Data.Sprites.FirstOrDefault(x => x.Name.Content == baseName)
           ?? Data.Sprites.FirstOrDefault(x => x.Name.Content == baseName + "_en");
    if (src == null)
    {
        Console.WriteLine($"  ПРОПУСК {s.Name.Content}: нет EN-источника ({baseName}[_en])");
        skipped++;
        continue;
    }

    int n = Math.Min(s.Textures.Count, src.Textures.Count);
    int f = 0;
    for (int i = 0; i < n; i++)
    {
        var srcTex = src.Textures[i]?.Texture;
        if (srcTex == null || s.Textures[i] == null) continue;
        s.Textures[i].Texture = srcTex;   // делим тот же texture page item, что и база
        f++; frames++;
    }
    Console.WriteLine($"  {s.Name.Content,-42} <- {src.Name.Content,-40} кадров:{f}"
        + (n < s.Textures.Count ? $"  (у _ja кадров {s.Textures.Count}, у базы {src.Textures.Count})" : ""));
    swapped++;
}

Console.WriteLine($"подменено спрайтов: {swapped}, кадров: {frames}, пропущено (нет EN): {skipped}");
Console.WriteLine("SWAP DONE");
