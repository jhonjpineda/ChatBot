import { useMemo } from 'react';

export interface WordCloudWord {
  word: string;
  count: number;
  weight: number; // 0-1
}

interface WordCloudProps {
  words: WordCloudWord[];
  maxWords?: number;
  minFontSize?: number;
  maxFontSize?: number;
  colors?: string[];
}

export default function WordCloud({
  words,
  maxWords = 50,
  minFontSize = 14,
  maxFontSize = 48,
  colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'],
}: WordCloudProps) {
  // Procesar palabras para la visualización
  const processedWords = useMemo(() => {
    const displayWords = words.slice(0, maxWords);

    return displayWords.map((wordData, index) => {
      // Calcular tamaño de fuente basado en peso
      const fontSize = minFontSize + (maxFontSize - minFontSize) * wordData.weight;

      // Asignar color basado en frecuencia
      const colorIndex = Math.floor((wordData.weight * (colors.length - 1)));
      const color = colors[colorIndex];

      // Posición semi-aleatoria pero determinística
      const seed = wordData.word.charCodeAt(0) + index;
      const x = (seed * 37) % 90 + 5; // 5-95%
      const y = (seed * 47) % 90 + 5; // 5-95%

      return {
        ...wordData,
        fontSize: Math.round(fontSize),
        color,
        x,
        y,
      };
    });
  }, [words, maxWords, minFontSize, maxFontSize, colors]);

  if (words.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-500">
            No hay datos suficientes para generar la nube de palabras
          </p>
          <p className="text-xs text-gray-400 mt-1">
            Haz algunas preguntas al chatbot para ver las palabras más frecuentes
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-96 bg-gradient-to-br from-gray-50 to-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Grid layout approach for word cloud */}
      <div className="absolute inset-0 p-8 flex flex-wrap items-center justify-center gap-3">
        {processedWords.map((word, index) => (
          <div
            key={`${word.word}-${index}`}
            className="group relative inline-block cursor-pointer transition-all duration-200 hover:scale-110"
            style={{
              fontSize: `${word.fontSize}px`,
              color: word.color,
              fontWeight: word.weight > 0.7 ? 700 : word.weight > 0.4 ? 600 : 500,
            }}
          >
            {word.word}

            {/* Tooltip on hover */}
            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
              <div className="font-semibold">{word.count} veces</div>
              <div className="text-gray-300">
                {(word.weight * 100).toFixed(0)}% de frecuencia
              </div>
              {/* Arrow */}
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        ))}
      </div>

      {/* Leyenda de colores */}
      <div className="absolute bottom-2 right-2 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm">
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <span className="font-medium">Frecuencia:</span>
          <div className="flex gap-1">
            {colors.map((color, i) => (
              <div
                key={color}
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: color }}
                title={
                  i === colors.length - 1
                    ? 'Muy frecuente'
                    : i === 0
                    ? 'Poco frecuente'
                    : 'Media'
                }
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
