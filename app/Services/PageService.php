<?php

namespace App\Services;

use App\Contracts\BaseService;
use App\Http\Resources\V1\PageResource;
use App\Models\Page;

class PageService
{
    public function __construct(protected BaseService $baseService) {}

    public function fetch(Page $page)
    {
        return ($this->baseService)(function () use ($page) {
            $page->load([
                'verses' => function ($query) {
                    $query->orderBy('local_number');
                },
                'verses.words' => function ($query) {
                    $query->orderBy('position');
                },
                'verses.surah',
                'verses.hizb',
                'verses.juz',
            ])->toResource(PageResource::class);

            return $page;
        });
    }
}
