USE cms;
CREATE TABLE cms.RPT (
       RPT_REC_NUM          BIGINT NOT NULL,
       PRVDR_CTRL_TYPE_CD   CHAR(25) NULL,
       PRVDR_NUM            CHAR(25) NOT NULL,
       NPI                  BIGINT NULL,
       RPT_STUS_CD          CHAR(25) NOT NULL,
       FY_BGN_DT            DATE NULL,
       FY_END_DT            DATE NULL,
       PROC_DT              DATE NULL,
       INITL_RPT_SW         CHAR(25) NULL,
       LAST_RPT_SW          CHAR(25) NULL,
       TRNSMTL_NUM          CHAR(25) NULL,
       FI_NUM               CHAR(25) NULL,
       ADR_VNDR_CD          CHAR(25) NULL,
       FI_CREAT_DT          DATE NULL,
       UTIL_CD              CHAR(25) NULL,
       NPR_DT               DATE NULL,
       SPEC_IND             CHAR(25) NULL,
       FI_RCPT_DT           DATE NULL
);

CREATE TABLE cms.RPT_ALPHA (
       RPT_REC_NUM          BIGINT NOT NULL,
       WKSHT_CD             CHAR(25) NOT NULL,
       LINE_NUM             CHAR(25) NOT NULL,
       CLMN_NUM             CHAR(25) NOT NULL,   
       ALPHNMRC_ITM_TXT     CHAR(100) NULL
);

CREATE TABLE cms.RPT_NMRC (
       RPT_REC_NUM          BIGINT NOT NULL,
       WKSHT_CD             CHAR(25) NOT NULL,
       LINE_NUM             CHAR(25) NOT NULL,
       CLMN_NUM             CHAR(25) NOT NULL,	
       ITM_VAL_NUM          BIGINT NOT NULL
);
