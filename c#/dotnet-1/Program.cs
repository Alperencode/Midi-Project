// load score
var score = AlphaTab.Importer.ScoreLoader.LoadScoreFromBytes(File.ReadAllBytes(args[0]));

// render score with svg engine and desired rendering width
var settings = new AlphaTab.Settings();
settings.Core.Engine = "skia";
var renderer = new AlphaTab.Rendering.ScoreRenderer(settings)
{
    Width = 970
};
var partialImages = new List<SKImage>();
var totalWidth = 0;
var totalHeight = 0;
renderer.PartialRenderFinished.On(r => { images.Add((SKImage) r.RenderResult); });
renderer.RenderFinished.On(r =>
{
    totalWidth = (int) r.TotalWidth;
    totalHeight = (int) r.TotalHeight;
});
renderer.RenderScore(score, new double[] { track.Index });