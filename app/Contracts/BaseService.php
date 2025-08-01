<?php

namespace App\Contracts;

use Illuminate\Contracts\Debug\ExceptionHandler;
use Illuminate\Support\Facades\DB;

class BaseService{

    public function __invoke(\Closure $action , ?\Closure $reject = null) {

        DB::beginTransaction();
        try {
            $result = $action();
            DB::commit();
        } catch (\Throwable $th) {
            DB::rollBack();
            !is_null($reject) && $reject();
            app()[ExceptionHandler::class]->report($th);
            return ApiResponseFacade::Message($th->getMessage())->Code(500)->response();
        }
        return ApiResponseFacade::Message('Operation Processed')->Code(200)->Data($result)->response();
    }
}
