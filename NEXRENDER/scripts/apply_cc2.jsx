(function applyCc2Preset() {
    var LAYER_NAME = "SRC";
    var PRESET_PATH = "C:\\nexrender\\presets\\cc2.ffx";

    function log(msg) {
        $.writeln("[apply_cc2] " + msg);
    }

    function fail(msg) {
        log("ERROR: " + msg);
        throw new Error("[apply_cc2] " + msg);
    }

    if (typeof app !== "undefined" && app.beginSuppressDialogs) {
        app.beginSuppressDialogs();
    }

    var presetFile = new File(PRESET_PATH);
    if (!presetFile.exists) {
        fail("preset introuvable: " + PRESET_PATH);
    }

    var comp = null;
    if (app.project.activeItem instanceof CompItem) {
        comp = app.project.activeItem;
    } else {
        var i;
        for (i = 1; i <= app.project.numItems; i++) {
            if (app.project.item(i) instanceof CompItem) {
                comp = app.project.item(i);
                break;
            }
        }
    }

    if (!(comp instanceof CompItem)) {
        fail("aucune composition trouvee dans le projet");
    }

    var layer = null;
    var j;
    for (j = 1; j <= comp.numLayers; j++) {
        if (comp.layer(j).name === LAYER_NAME) {
            layer = comp.layer(j);
            break;
        }
    }

    if (!layer) {
        fail("calque '" + LAYER_NAME + "' introuvable dans '" + comp.name + "'");
    }

    try {
        layer.applyPreset(presetFile);
        log("preset cc2.ffx applique sur " + LAYER_NAME + " dans " + comp.name);
    } catch (e) {
        fail("applyPreset a echoue (plugin manquant ?): " + e.toString());
    }
})();
