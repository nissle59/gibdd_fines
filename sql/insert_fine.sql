INSERT INTO
			fines_base.fines(
				discount_date, -- DateDiscount
				law,           -- KoAPcode . replace('ч.','.')
				division_id,   -- Division
				create_time,    -- DateDecis
				discount_expire_days, -- (DateDiscount) - now() if > 0
				total_amount,         -- if(enableDisount): Summa / 2 else: Summa
				amount_to_pay,        -- if(enableDisount): Summa / 2 else: Summa
				resolution_number,    -- SupplierBillID
				law_description,      -- KoAPtext
                is_active_discount, -- enableDiscount
                sts_number,
                offence_at,
                resolution_date,
                transfer_fssp_date,
                from_gibdd,
                penalty_date,
                pics_token
			) 
		VALUES (
			$1::timestamp,	--discount_date			:: int4->timestamp
			$2,					--law					:: text
            $3,                 --division_id      	    :: int4(8)
                   --$4,	                --description		    :: text
            $5::timestamp, --create_time	        :: int4->timestamp
			$6,					--discount_expire_days	:: int4
			$7,					--total_amount			:: int4
			$7,	                --amount_to_pay         :: int4
			$8,					--resolution_number		:: text
			$4,	                --law_description		:: text
            $9, --is_active_discount	:: bool
            $10,
            $5::timestamp,
            $11::date,
            $12::date,
            true,
            $5::timestamp,
            $13
		) 
		on conflict (resolution_number) 
		do update set
		    discount_date = $1::timestamp, -- DateDiscount
            law = $2,           -- KoAPcode . replace('ч.','.')
            division_id = $3::int4,   -- Division
                       --description = $4,    -- KoAPtext
            create_time = $5::timestamp,    -- DateDecis
            discount_expire_days =$6::int4, -- (DateDiscount) - now() if > 0
            total_amount = $7::int4,         -- if(enableDisount): Summa / 2 else: Summa
            amount_to_pay = $7::int4,        -- if(enableDisount): Summa / 2 else: Summa
            law_description = $4,      -- KoAPtext
            is_active_discount = $9, -- enableDiscount
            sts_number      = $10, -- sts
            offence_at      = $5::timestamp, --DateDecis
            resolution_date = $11::date, --DatePost
            transfer_fssp_date = $12::date, --DateSSP
            from_gibdd   = true,
            penalty_date = $5::timestamp,
            pics_token   = $13
		RETURNING 
			resolution_number,
            amount_to_pay,
            status