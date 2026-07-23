using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using UndertaleModLib;
using UndertaleModLib.Models;
using UndertaleModLib.Util;

// Экспорт локализуемых спрайтов в sprites/: <имя>_<кадр>.png — их перерисовывают
// на русский и вшивают import_sprites.csx. Локаль в игре показывает японские версии
// (spr_X_ja / spr_X_jp); мы редактируем АНГЛИЙСКИЙ источник (spr_X либо spr_X_en),
// а texture_swap_ja.csx направляет _ja/_jp на него.
//
// Набор находится ДИНАМИЧЕСКИ: для каждого spr_*_ja / spr_*_jp берём английский
// источник; если его нет (чисто японский спрайт) — сам _ja (редроу поверх японского).
// Плюс явный список ниже — спрайты, что подменяются через карту scr_84 без _ja-двойника.
// СУЩЕСТВУЮЩИЕ PNG НЕ ПЕРЕЗАПИСЫВАЕМ (чтобы не затереть готовый русский редроу).

string outDir = "/Users/mtglitch/deltarune-ch5-ru/sprites";
Directory.CreateDirectory(outDir);

// спрайты, локализуемые через карту (нет _ja-двойника в ассетах)
string[] mapOnly = {
    "spr_bnamekris", "spr_bnameralsei", "spr_bnamesusie", "spr_bnamenoelle",
    "spr_battlemsg", "spr_btact", "spr_btdefend", "spr_btfight", "spr_btitem",
    "spr_btspare", "spr_bttech", "spr_darkmenudesc", "spr_dmenu_captions",
    "spr_quitmessage", "spr_fieldmuslogo", "spr_shop_space_ui",
    "spr_funnytext_ass", "spr_face_queen",
};

var targets = new SortedSet<string>(mapOnly);
var suffix = new Regex("_(ja|jp)$");
bool Has(string n) => Data.Sprites.Any(x => x.Name.Content == n);

foreach (var s in Data.Sprites.Where(x => suffix.IsMatch(x.Name.Content)))
{
    string b = suffix.Replace(s.Name.Content, "");
    if (Has(b)) targets.Add(b);                 // английская база spr_X
    else if (Has(b + "_en")) targets.Add(b + "_en");  // либо spr_X_en
    else targets.Add(s.Name.Content);           // чисто японский — редроу поверх _ja
}

int wrote = 0, kept = 0, missing = 0;
using (var tw = new TextureWorker())
{
    foreach (var name in targets)
    {
        var s = Data.Sprites.FirstOrDefault(x => x.Name.Content == name);
        if (s == null) { Console.WriteLine($"НЕ НАЙДЕН: {name}"); missing++; continue; }
        for (int i = 0; i < s.Textures.Count; i++)
        {
            var t = s.Textures[i]?.Texture;
            if (t == null) continue;
            string path = $"{outDir}/{name}_{i}.png";
            if (File.Exists(path)) { kept++; continue; }   // не трогаем существующий редроу
            tw.GetTextureFor(t, name, true).Write(path);
            wrote++;
        }
    }
}
Console.WriteLine($"локализуемых спрайтов: {targets.Count}");
Console.WriteLine($"новых PNG: {wrote}, сохранено существующих: {kept}, не найдено: {missing}");
Console.WriteLine("EXPORT SPRITES DONE");
