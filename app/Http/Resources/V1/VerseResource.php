<?php

namespace App\Http\Resources\V1;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class VerseResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'verse_number' => $this->verse_number,
            'text' => $this->text,
            'words' => WordResource::collection($this->words),
            'surah' => new SurahResource($this->whenLoaded('surah')),
            'juz' => new JuzResource($this->whenLoaded('juz')),
            'hizb' => new HizbResource($this->whenLoaded('hizb')),
        ];
    }
}
