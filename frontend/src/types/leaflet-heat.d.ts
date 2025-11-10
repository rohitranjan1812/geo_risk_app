declare module 'leaflet.heat' {
  import * as L from 'leaflet';

  interface HeatLayerOptions extends L.LayerOptions {
    minOpacity?: number;
    maxZoom?: number;
    max?: number;
    radius?: number;
    blur?: number;
    gradient?: { [key: number]: string };
  }

  function heatLayer(
    latlngs: Array<[number, number, number]>,
    options?: HeatLayerOptions
  ): L.Layer;

  namespace L {
    function heatLayer(
      latlngs: Array<[number, number, number]>,
      options?: HeatLayerOptions
    ): Layer;
  }
}
