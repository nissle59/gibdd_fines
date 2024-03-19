INSERT INTO
			fines_base.fines(
				discount_date, -- DateDiscount
				law,           -- KoAPcode . replace('ч.','.')
				division_id,   -- Division
				description,    -- KoAPtext
				create_time,    -- DateDecis
				discount_expire_days, -- (DateDiscount) - now() if > 0
				total_amount,         -- if(enableDisount): Summa / 2 else: Summa
				amount_to_pay,        -- if(enableDisount): Summa / 2 else: Summa
				resolution_number,    -- SupplierBillID
				law_description,      -- KoAPtext
				is_active_discount    -- enableDiscount
			) 
		VALUES (
			to_timestamp($1),	--discount_date			:: int4->timestamp
			$2,					--law					:: text
            $3,                 --division_id      	    :: int4(8)
			$4,	                --description		    :: text
            to_timestamp($5)  , --create_time	        :: int4->timestamp
			$6,					--discount_expire_days	:: int4
			$7,					--total_amount			:: int4
			$7,	                --amount_to_pay         :: int4
			$8,					--resolution_number		:: text
			$4,	                --law_description		:: text
			$9	            --is_active_discount	:: bool
            --to_timestamp($11)   --
		) 
		on conflict (resolution_number) 
		do update set
		    discount_date = 	to_timestamp($1), -- DateDiscount
            law = $2,           -- KoAPcode . replace('ч.','.')
            division_id = $3,   -- Division
            description = $4,    -- KoAPtext
            create_time = $5,    -- DateDecis
            discount_expire_days =$6, -- (DateDiscount) - now() if > 0
            total_amount = $7,         -- if(enableDisount): Summa / 2 else: Summa
            amount_to_pay = $8,        -- if(enableDisount): Summa / 2 else: Summa
            law_description = $10,      -- KoAPtext
            is_active_discount = $11    -- enableDiscount
		RETURNING 
			resolution_number,
            amount_to_pay,
            status