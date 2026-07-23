using System;
using System.Linq;
using UndertaleModLib;
using UndertaleModLib.Models;

string Tex(UndertaleSprite s, int f) =>
    (s != null && f < s.Textures.Count) ? (s.Textures[f]?.Texture?.Name?.Content ?? "null") : "-";

int ok = 0, bad = 0;
foreach (var pair in new[]{
    ("spr_green_sign_ja","spr_green_sign"),
    ("spr_green_sign_big_jp","spr_green_sign_big"),
    ("spr_flowershop_ja","spr_flowershop"),
    ("spr_gardenmuslogo_ja","spr_gardenmuslogo"),
    ("spr_dw_fcastle_second_diner_sign_ja","spr_dw_fcastle_second_diner_sign_en"),
})
{
    var ja = Data.Sprites.FirstOrDefault(x => x.Name.Content == pair.Item1);
    var bs = Data.Sprites.FirstOrDefault(x => x.Name.Content == pair.Item2);
    string tja = Tex(ja,0), tbs = Tex(bs,0);
    bool same = tja == tbs && tja != "null" && tja != "-";
    Console.WriteLine($"{(same?"OK ":"BAD")} {pair.Item1}[0]={tja}  == {pair.Item2}[0]={tbs}");
    if (same) ok++; else bad++;
}
Console.WriteLine($"SWAP VERIFY: ok={ok} bad={bad}");
